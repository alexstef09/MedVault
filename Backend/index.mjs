import express from 'express';
import multer from 'multer';
import dotenv from 'dotenv';
import { ethers } from 'ethers';
import uploadToIPFS from './utils/uploadToIPFS.js';
import fs from 'fs';
import jwt from 'jsonwebtoken';
import sqlite3 from 'sqlite3';
import { recoverAddress } from 'ethers';
import { open } from 'sqlite';
import downloadRoute from './routes/download.js';
import createAuthRoutes from './routes/authRoutes.js';
import { encrypt, decrypt } from './utils/crypto.js';
import loadDecryptedPrivateKey from './utils/loadPrivateKey.js';

dotenv.config();

const {
  ENCRYPTED_KEY_PATH,
  KEY_PASSPHRASE,
  CONTRACT_ADDRESS,
  JWT_SECRET = 'supersecret',
  RPC_URL = 'http://localhost:8545'
} = process.env;

if (!ENCRYPTED_KEY_PATH || !KEY_PASSPHRASE || !CONTRACT_ADDRESS) {
  throw new Error('❌ Missing ENCRYPTED_KEY_PATH, KEY_PASSPHRASE, or CONTRACT_ADDRESS in .env');
}

const ABI = JSON.parse(fs.readFileSync('./utils/MedVaultABI.json', 'utf8'));
const app = express();
const port = 3000;
app.use(express.json());
const upload = multer({ dest: 'uploads/' });

const provider = new ethers.JsonRpcProvider(RPC_URL);
const privateKey = loadDecryptedPrivateKey(ENCRYPTED_KEY_PATH, KEY_PASSPHRASE);
const wallet = new ethers.Wallet(privateKey, provider);
const medVault = new ethers.Contract(CONTRACT_ADDRESS, ABI, wallet);
const actualAdmin = await medVault.admin();
console.log("✅ Smart contract admin is:", actualAdmin);

const db = await open({ filename: './medvault.db', driver: sqlite3.Database });
await db.exec(`
  CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient TEXT NOT NULL,         -- encrypted
    patientName TEXT NOT NULL,     -- encrypted
    patientID TEXT NOT NULL,       -- encrypted
    ipfsHash TEXT NOT NULL,        -- plain
    uploadedBy TEXT NOT NULL,      -- plain
    timestamp TEXT NOT NULL        -- plain
  );

  CREATE UNIQUE INDEX IF NOT EXISTS unique_record_constraint
  ON records (patient, ipfsHash, uploadedBy, timestamp);

  CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accessor TEXT,
    patient TEXT,
    timestamp TEXT
  );

  CREATE TABLE IF NOT EXISTS doctors (
    address TEXT PRIMARY KEY,
    approvedAt TEXT
  );

  CREATE TABLE IF NOT EXISTS users (
    address TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'doctor', 'staff'))
  );
`);

function authenticateJWT(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Missing token' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid token' });
    req.user = user;
    next();
  });
}

app.post('/auth/staff-verify', async (req, res) => {
  const { name, address, signature, nonce } = req.body;

  if (!name || !address || !signature || !nonce) {
    return res.status(400).json({ error: 'Missing required fields.' });
  }

  try {
    const message = `Sign this nonce to authenticate: ${nonce}`;
    const msgHash = ethers.hashMessage(message);
    const sig = signature.startsWith("0x") ? signature : "0x" + signature;
    const recovered = recoverAddress(msgHash, sig).toLowerCase();

    if (recovered !== address.toLowerCase()) {
      return res.status(401).json({ error: 'Signature does not match address.' });
    }

    const user = await db.get(
      'SELECT * FROM users WHERE LOWER(name) = ? AND LOWER(address) = ?',
      [name.toLowerCase(), address.toLowerCase()]
    );

    if (!user) {
      return res.status(403).json({ error: 'No such user found with matching name and address.' });
    }

    const token = jwt.sign({ address, name: user.name, role: user.role }, JWT_SECRET, { expiresIn: '2h' });
    res.json({ token });

  } catch (err) {
    console.error('❌ STAFF login error:', err);
    res.status(500).json({ error: 'STAFF login failed', details: err.message });
  }
});

app.post('/upload', authenticateJWT, upload.single('record'), async (req, res) => {
  console.log("📥 Upload route hit by:", req.user?.address);
  try {
    const uploaderAddress = req.user.address.toLowerCase();
    const contractAdmin = (await medVault.admin()).toLowerCase();
    const isDoctor = await medVault.isDoctor(uploaderAddress);

    if (uploaderAddress !== contractAdmin && !isDoctor) {
      return res.status(403).json({ error: 'Unauthorized: Only approved doctors or admin can upload records.' });
    }

    const { patientName, patientID } = req.body;
    if (!patientName || !patientID) {
      return res.status(400).json({ error: 'Missing patient name or ID.' });
    }

    const buffer = fs.readFileSync(req.file.path);
    const cid = await uploadToIPFS(buffer);
    const tx = await medVault.uploadRecord(uploaderAddress, cid);
    await tx.wait();

    const timestamp = new Date().toISOString();
    await db.run(`
      INSERT INTO records (patient, patientName, patientID, ipfsHash, uploadedBy, timestamp)
      VALUES (?, ?, ?, ?, ?, ?)
    `, [
      encrypt(uploaderAddress),         // patient address (encrypted)
      encrypt(patientName),
      encrypt(patientID),
      cid,                              // store plain CID (NOT encrypted)
      uploaderAddress,                  // store plain uploader address (NOT encrypted)
      timestamp
    ]);

    console.log("✅ Record inserted into DB for:", uploaderAddress);
    res.json({ message: '✅ File uploaded and stored successfully.', cid, txHash: tx.hash });

  } catch (error) {
    console.error('❌ Upload failed:', error);
    res.status(500).json({ error: 'Upload failed', details: error.message });
  }
});


app.get('/lookup/name/:name', authenticateJWT, async (req, res) => {
  try {
    const { name } = req.params;
    const dbRows = await db.all('SELECT * FROM records');

    const matched = dbRows.filter(row => {
      try {
        return decrypt(row.patientName).toLowerCase() === name.toLowerCase();
      } catch {
        return false;
      }
    });

    const records = matched.map(row => ({
      patientName: decrypt(row.patientName),
      patientID: decrypt(row.patientID),
      ipfsHash: row.ipfsHash,
      uploadedBy: row.uploadedBy,
      timestamp: row.timestamp
    }));

    res.json({ recordCount: records.length, records });
  } catch (error) {
    console.error("❌ Lookup by name failed:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});


app.post('/users', authenticateJWT, async (req, res) => {
  try {
    const { address, name, role } = req.body;
    const admin = await medVault.admin();
    if (req.user.address.toLowerCase() !== admin.toLowerCase()) {
      return res.status(403).json({ error: 'Unauthorized: Only admin can register users.' });
    }
    if (!address || !name || !role) {
      return res.status(400).json({ error: 'Missing user data (address, name, or role).' });
    }
    await db.run('INSERT OR REPLACE INTO users (address, name, role) VALUES (?, ?, ?)', [
      address.toLowerCase(), name, role
    ]);
    res.json({ message: 'User registered or updated successfully.' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to register user', details: error.message });
  }
});

app.get('/users', authenticateJWT, async (req, res) => {
  try {
    const admin = await medVault.admin();
    if (req.user.address.toLowerCase() !== admin.toLowerCase()) {
      return res.status(403).json({ error: 'Unauthorized: Only admin can view users.' });
    }
    const users = await db.all('SELECT * FROM users ORDER BY role');
    res.json({ users });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch users', details: error.message });
  }
});


app.get('/doctor-dashboard', authenticateJWT, async (req, res) => {
  try {
    const doctorAddress = req.user.address.toLowerCase();
    const allRecords = await db.all(`SELECT patient, uploadedBy FROM records`);

    const summary = {};

    for (const row of allRecords) {
      // ✅ uploadedBy is now plain text, no need to decrypt it
      if (row.uploadedBy.toLowerCase() === doctorAddress) {
        const decryptedPatient = decrypt(row.patient); // patient is still encrypted
        summary[decryptedPatient] = (summary[decryptedPatient] || 0) + 1;
      }
    }

    const patients = Object.entries(summary).map(([patient, recordCount]) => ({
      patient,
      recordCount
    }));

    res.json({ patients });
  } catch (error) {
    console.error('❌ Doctor dashboard error:', error);
    res.status(500).json({ error: 'Dashboard failed', details: error.message });
  }
});



app.get('/records/:patientAddress', authenticateJWT, async (req, res) => {
  try {
    const { patientAddress } = req.params;
    const accessor = req.user.address.toLowerCase();

    const total = parseInt((await medVault.getRecordCount(patientAddress)).toString());
    const chainRecords = [];

    for (let i = 0; i < total; i++) {
      const [ipfsHash, uploadedBy, timestamp] = await medVault.getRecord(patientAddress, i);
      chainRecords.push({
        ipfsHash,
        uploadedBy: uploadedBy.toLowerCase(),
        timestamp: new Date(Number(timestamp) * 1000).toISOString()
      });
    }

    // Log audit
    await db.run('INSERT INTO audit_logs (accessor, patient, timestamp) VALUES (?, ?, ?)', [
      encrypt(accessor), encrypt(patientAddress), new Date().toISOString()
    ]);

    // Role
    const contractAdmin = (await medVault.admin()).toLowerCase();
    let role = accessor === contractAdmin ? 'admin' : 'unknown';

    if (role !== 'admin') {
      const userRow = await db.get('SELECT role FROM users WHERE address = ?', [accessor]);
      if (userRow?.role) role = userRow.role;
    }

    const dbRows = await db.all('SELECT * FROM records');
    const enrichedRecords = [];

    for (const rec of chainRecords) {
      const match = dbRows.find(row => {
        try {
          return (
            decrypt(row.patient).toLowerCase() === patientAddress.toLowerCase() &&
            row.ipfsHash === rec.ipfsHash
          );
        } catch {
          return false;
        }
      });

      let patientName = 'Unknown';
      let patientID = 'Unknown';
      let uploaderName = 'Unassigned';

      if (match) {
        try { patientName = decrypt(match.patientName); } catch {}
        try { patientID = decrypt(match.patientID); } catch {}
      }

      const uploader = await db.get('SELECT name FROM users WHERE address = ?', [rec.uploadedBy]);
      if (uploader?.name) uploaderName = uploader.name;

      enrichedRecords.push({
        patientName,
        patientID,
        ipfsHash: rec.ipfsHash,
        uploadedBy: rec.uploadedBy,
        uploaderName,
        timestamp: rec.timestamp
      });
    }

    if (role === 'admin') {
      return res.json({
        patient: patientAddress,
        count: enrichedRecords.length,
        records: enrichedRecords.map(r => ({
          patientName: r.patientName,
          patientID: r.patientID,
          ipfsHash: r.ipfsHash,
          uploadedBy: `${r.uploaderName} (${r.uploadedBy})`,
          timestamp: r.timestamp
        }))
      });
    } else if (['doctor', 'staff'].includes(role)) {
      return res.json({
        patient: patientAddress,
        count: enrichedRecords.length,
        records: enrichedRecords.map(r => ({
          patientName: r.patientName,
          patientID: r.patientID,
          ipfsHash: r.ipfsHash,
          uploaderName: r.uploaderName,
          timestamp: r.timestamp
        }))
      });
    } else {
      return res.status(403).json({ error: "Access denied: unrecognized role." });
    }

  } catch (error) {
    console.error('❌ Failed to fetch records:', error);
    res.status(500).json({ error: 'Could not retrieve records', details: error.message });
  }
});



app.post('/approve-doctor', authenticateJWT, async (req, res) => {
  try {
    const { doctorAddress } = req.body;
    const adminAddress = req.user.address;
    const contractAdmin = await medVault.admin();
    if (adminAddress.toLowerCase() !== contractAdmin.toLowerCase()) {
      return res.status(403).json({ error: 'Unauthorized: Only admin can approve doctors.' });
    }
    const tx = await medVault.addDoctor(doctorAddress);
    await tx.wait();
    await db.run('INSERT OR REPLACE INTO doctors (address, approvedAt) VALUES (?, ?)', [
      doctorAddress.toLowerCase(), new Date().toISOString()
    ]);
    res.json({ message: 'Doctor approved successfully', doctorAddress });
  } catch (error) {
    console.error('❌ Approval failed:', error);
    res.status(500).json({ error: 'Approval failed', details: error.message });
  }
});

app.post('/revoke-doctor', authenticateJWT, async (req, res) => {
  try {
    const { doctorAddress } = req.body;
    const adminAddress = req.user.address;
    const contractAdmin = await medVault.admin();
    if (adminAddress.toLowerCase() !== contractAdmin.toLowerCase()) {
      return res.status(403).json({ error: 'Unauthorized: Only admin can revoke doctors.' });
    }
    const tx = await medVault.removeDoctor(doctorAddress);
    await tx.wait();
    await db.run('DELETE FROM doctors WHERE address = ?', [doctorAddress.toLowerCase()]);
    res.json({ message: 'Doctor revoked successfully', doctorAddress });
  } catch (error) {
    console.error('❌ Revocation failed:', error);
    res.status(500).json({ error: 'Revocation failed', details: error.message });
  }
});

app.get('/doctors', authenticateJWT, async (req, res) => {
  try {
    const rows = await db.all('SELECT * FROM doctors ORDER BY approvedAt DESC');
    res.json({ doctors: rows });
  } catch (error) {
    res.status(500).json({ error: 'Doctor list fetch failed', details: error.message });
  }
});

app.get('/audit-log', authenticateJWT, async (req, res) => {
  try {
    const isAdmin = await medVault.admin();
    if (req.user.address.toLowerCase() !== isAdmin.toLowerCase()) {
      return res.status(403).json({ error: 'Access denied. Admins only.' });
    }
    const logs = await db.all('SELECT * FROM audit_logs ORDER BY timestamp DESC');
    const decryptedLogs = logs.map(log => ({
      id: log.id,
      accessor: decrypt(log.accessor),
      patient: decrypt(log.patient),
      timestamp: log.timestamp
    }));
    res.json({ count: decryptedLogs.length, log: decryptedLogs });
  } catch (error) {
    res.status(500).json({ error: 'Audit log fetch failed', details: error.message });
  }
});

app.use('/download', downloadRoute);
app.use('/auth', createAuthRoutes(db));

app.get('/users', async (req, res) => {
  try {
    const rows = await db.all('SELECT name, address, role FROM users');
    res.json({ users: rows });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch users', details: error.message });
  }
});

app.listen(port, () => {
  console.log(`🚀 Server running at http://localhost:${port}`);
});
