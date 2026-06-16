import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

const migrate = async () => {
  const db = await open({ filename: './medvault.db', driver: sqlite3.Database });

  try {
    const columns = await db.all(`PRAGMA table_info(records);`);
    const columnNames = columns.map(col => col.name.toLowerCase());

    if (!columnNames.includes('patient')) {
      await db.exec(`ALTER TABLE records ADD COLUMN patient TEXT;`);
      console.log("✅ Added column: patient");
    }

    if (!columnNames.includes('patientname')) {
      await db.exec(`ALTER TABLE records ADD COLUMN patientName TEXT;`);
      console.log("✅ Added column: patientName");
    }

    if (!columnNames.includes('patientid')) {
      await db.exec(`ALTER TABLE records ADD COLUMN patientID TEXT;`);
      console.log("✅ Added column: patientID");
    }

    if (!columnNames.includes('ipfshash')) {
      await db.exec(`ALTER TABLE records ADD COLUMN ipfsHash TEXT;`);
      console.log("✅ Added column: ipfsHash");
    }

    if (!columnNames.includes('uploadedby')) {
      await db.exec(`ALTER TABLE records ADD COLUMN uploadedBy TEXT;`);
      console.log("✅ Added column: uploadedBy");
    }

    if (!columnNames.includes('timestamp')) {
      await db.exec(`ALTER TABLE records ADD COLUMN timestamp TEXT;`);
      console.log("✅ Added column: timestamp");
    }

    // Add unique index if not exists
    const existingIndexes = await db.all(`PRAGMA index_list(records);`);
    const hasUniqueIndex = existingIndexes.some(index => index.name === 'unique_record_constraint');

    if (!hasUniqueIndex) {
      await db.exec(`
        CREATE UNIQUE INDEX unique_record_constraint
        ON records (patient, ipfsHash, uploadedBy, timestamp);
      `);
      console.log("✅ Added UNIQUE constraint to records.");
    }

    console.log("✅ Migration complete.");
  } catch (err) {
    console.error("❌ Migration error:", err.message);
  } finally {
    await db.close();
  }
};

migrate();
