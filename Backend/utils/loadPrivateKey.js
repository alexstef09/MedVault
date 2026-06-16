import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

export default function loadDecryptedPrivateKey() {
  const { KEY_PASSPHRASE } = process.env;
  const filePath = path.resolve(process.env.ENCRYPTED_KEY_PATH);
  const { ciphertext, salt, iv } = JSON.parse(fs.readFileSync(filePath));

  const key = crypto.scryptSync(KEY_PASSPHRASE, Buffer.from(salt, 'hex'), 32);
  const decipher = crypto.createDecipheriv(
    'aes-256-cbc',
    key,
    Buffer.from(iv, 'hex')
  );

  const decrypted = Buffer.concat([
    decipher.update(Buffer.from(ciphertext, 'hex')),
    decipher.final()
  ]);

  return decrypted.toString('utf8'); // this is your real private key
}
