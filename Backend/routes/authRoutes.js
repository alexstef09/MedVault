import express from 'express';
import { ethers } from 'ethers';
import jwt from 'jsonwebtoken';

const nonces = new Map();
const loginNonces = {};
const JWT_SECRET = process.env.JWT_SECRET || 'supersecret';

export default function authRoutes(db) {
  const router = express.Router();

  router.get('/challenge', (req, res) => {
    const address = req.query.address;
    if (!address || !ethers.isAddress(address)) {
      return res.status(400).json({ error: 'Invalid Ethereum address' });
    }
    const nonce = `Sign this nonce to authenticate: ${Math.floor(Math.random() * 1e6)}`;
    nonces.set(address.toLowerCase(), nonce);
    loginNonces[address.toLowerCase()] = nonce;
    res.json({ address, nonce });
  });

router.post('/verify', async (req, res) => {
  const { address, signature } = req.body;

  if (!address || !signature) {
    return res.status(400).json({ error: 'Missing address or signature' });
  }

  const nonce = nonces.get(address.toLowerCase());
  if (!nonce) {
    return res.status(400).json({ error: 'No nonce found. Please request one first.' });
  }

  try {
    const fullMessage = `Sign this nonce to authenticate: ${nonce}`;
    const recovered = ethers.verifyMessage(
      fullMessage,
      signature.startsWith("0x") ? signature : "0x" + signature
    );

    if (recovered.toLowerCase() !== address.toLowerCase()) {
      return res.status(401).json({ error: 'Signature verification failed' });
    }

    const token = jwt.sign({ address }, JWT_SECRET, { expiresIn: '1h' });
    nonces.delete(address.toLowerCase());

    res.json({ message: 'Authentication successful', token });
  } catch (err) {
    res.status(500).json({ error: 'Verification failed', details: err.message });
  }
});

  router.post('/staff-verify', async (req, res) => {
    const { address, name, signature } = req.body;
    if (!address || !name || !signature) {
      return res.status(400).json({ error: 'Missing required fields.' });
    }
    try {
      const user = await db.get('SELECT * FROM users WHERE LOWER(name) = ? AND LOWER(address) = ?', [
        name.toLowerCase(), address.toLowerCase()
      ]);
      if (!user) {
        return res.status(404).json({ error: 'User not found or key does not match registered address.' });
      }
      const nonce = loginNonces[address.toLowerCase()];
      if (!nonce) {
        return res.status(400).json({ error: 'Missing nonce. Start login again.' });
      }
      const recovered = ethers.verifyMessage(nonce, signature);
      if (recovered.toLowerCase() !== address.toLowerCase()) {
        return res.status(401).json({ error: 'Invalid signature' });
      }
      const token = jwt.sign({ address, role: user.role, name: user.name }, JWT_SECRET, { expiresIn: '2h' });
      delete loginNonces[address.toLowerCase()];
      return res.json({ token });
    } catch (err) {
      console.error("❌ Staff verify error:", err);
      res.status(500).json({ error: 'Internal error', details: err.message });
    }
  });

  return router;
}
