import { ethers } from 'ethers';
import axios from 'axios';

const address = '0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199';
const privateKey = '0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e';
const nonce = 'Sign this nonce to authenticate: 235859'; // copy-paste from /auth/challenge

async function signAndVerify() {
  try {
    const wallet = new ethers.Wallet(privateKey);
    const signature = await wallet.signMessage(nonce);

    console.log('🔐 Signature:', signature);

    const response = await axios.post('http://localhost:3000/auth/verify', {
      address,
      signature
    });

    console.log('✅ Verified:', response.data);
  } catch (err) {
    console.error('❌ Error:', err.response?.data || err.message);
  }
}

signAndVerify();
