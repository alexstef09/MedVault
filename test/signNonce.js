// signNonce.js
import { ethers } from 'ethers';

// Use the private key for the address you're authenticating
const privateKey = '0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e'; // for 0x8626...
const wallet = new ethers.Wallet(privateKey);

// 👇 Paste the full nonce string returned from the GET /auth/challenge
const nonce = 'Sign this nonce to authenticate: 235859'; // replace with the actual one you got

async function main() {
  const signature = await wallet.signMessage(nonce);
  console.log("Signature:", signature);
}

main();
