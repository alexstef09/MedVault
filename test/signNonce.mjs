import { Wallet } from 'ethers';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const PRIVATE_KEY = process.env.PRIVATE_KEY;
if (!PRIVATE_KEY) throw new Error('❌ PRIVATE_KEY is missing in .env');

const wallet = new Wallet(PRIVATE_KEY);
const ADDRESS = wallet.address;

console.log('Wallet address:', ADDRESS);

const getNonce = async () => {
  const res = await axios.get(`http://localhost:3000/auth/challenge?address=${ADDRESS}`);
  return res.data.nonce;
};

const signAndVerify = async () => {
  const nonce = await getNonce();
  const signature = await wallet.signMessage(nonce);

  const verifyRes = await axios.post('http://localhost:3000/auth/verify', {
    address: ADDRESS,
    signature
  });

  console.log('✅ JWT:', verifyRes.data.token);
};

signAndVerify().catch(console.error);
