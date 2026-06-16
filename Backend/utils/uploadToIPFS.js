// utils/uploadToIPFS.js
import { create } from 'ipfs-http-client';

const ipfs = create({ url: 'http://localhost:5001' });

export default async function uploadToIPFS(originalBuffer) {
  // Force uniqueness by appending timestamp to buffer
  const uniqueBuffer = Buffer.concat([
    originalBuffer,
    Buffer.from(Date.now().toString()) // ⏱ makes each upload unique
  ]);

  const result = await ipfs.add(uniqueBuffer, { pin: true });

  console.log('✅ Uploaded to IPFS:', result.cid.toString());
  return result.cid.toV0().toString(); // Ensure Qm... format
}
