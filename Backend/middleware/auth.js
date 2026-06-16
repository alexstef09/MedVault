import { ethers } from 'ethers';
import fs from 'fs';
import dotenv from 'dotenv';

dotenv.config();

const ABI = JSON.parse(fs.readFileSync(new URL('../utils/MedVaultABI.json', import.meta.url)));
const contractAddress = process.env.CONTRACT_ADDRESS;
const provider = new ethers.JsonRpcProvider('http://localhost:8545');
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
const medVault = new ethers.Contract(contractAddress, ABI, wallet);

export const requireDoctor = async (req, res, next) => {
  try {
    const address = req.headers['x-wallet-address'];
    if (!address) return res.status(400).json({ error: 'Wallet address required in headers' });

    const isDoctor = await medVault.isDoctor(address);
    if (!isDoctor) return res.status(403).json({ error: 'Only approved doctors can perform this action' });

    next();
  } catch (err) {
    res.status(500).json({ error: 'Doctor check failed', details: err.message });
  }
};

export const requireAdmin = async (req, res, next) => {
  try {
    const address = req.headers['x-wallet-address'];
    if (!address) return res.status(400).json({ error: 'Wallet address required in headers' });

    const admin = await medVault.admin();
    if (address.toLowerCase() !== admin.toLowerCase()) {
      return res.status(403).json({ error: 'Only admin can perform this action' });
    }

    next();
  } catch (err) {
    res.status(500).json({ error: 'Admin check failed', details: err.message });
  }
};
