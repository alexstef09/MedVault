import express from 'express';
import axios from 'axios';

const router = express.Router();

router.get('/:cid', async (req, res) => {
  const cid = req.params.cid.trim();

 if (!cid || !/^[a-zA-Z0-9]+$/.test(cid.trim())) {
  return res.status(400).json({ error: 'Invalid CID' });
}


  try {
    const ipfsUrl = `http://127.0.0.1:8080/ipfs/${cid}`;
    const response = await axios.get(ipfsUrl, { responseType: 'stream' });

    res.setHeader('Content-Type', response.headers['content-type'] || 'application/octet-stream');
    res.setHeader('Content-Disposition', `attachment; filename=${cid}`);

    response.data.pipe(res);
  } catch (error) {
    console.error('❌ Failed to download from IPFS:', error.message);
    res.status(500).json({ error: 'Failed to fetch file from IPFS', details: error.message });
  }
});

export default router;
