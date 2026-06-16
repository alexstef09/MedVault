# 🏥 MedVault

A Blockchain-Based Cloud Solution for Hospital Patient Records

MedVault is a decentralized healthcare records management platform that combines Ethereum blockchain technology, IPFS distributed storage, and a desktop GUI application to provide secure, transparent, and tamper-proof patient record management.

## 🚀 Features

### 🔐 Secure Authentication
- Ethereum wallet-based authentication
- Cryptographic signature verification
- JWT session management
- Role-based access control

### 👨‍⚕️ Medical Record Management
- Upload encrypted patient records
- View patient history
- Retrieve records through IPFS
- Blockchain-backed audit trail

### 🏛 Role Management
- Admin-controlled doctor approval
- Doctor revocation functionality
- On-chain permission enforcement

### 📜 Audit & Compliance
- Immutable blockchain logging
- Full access tracking
- Record upload verification
- Transaction hash auditing

---

## 🏗 System Architecture

```text
┌─────────────────────┐
│     PyQt5 GUI       │
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│ Express.js Backend  │
└───────┬─────┬───────┘
        │     │
        │     │
        ▼     ▼
┌──────────┐ ┌──────────┐
│ Ethereum │ │   IPFS   │
│ Contract │ │ Storage  │
└──────────┘ └──────────┘
        │
        ▼
┌──────────┐
│ SQLite3  │
│ Database │
└──────────┘
```

---

## 🛠 Technologies Used

### Blockchain
- Solidity
- Ethereum
- Hardhat
- ethers.js

### Backend
- Node.js
- Express.js
- JWT Authentication

### Storage
- IPFS
- SQLite3

### Frontend
- Python
- PyQt5

---

## 📋 Prerequisites

Before running MedVault, install:

### Node.js
Version 18+

```bash
node -v
npm -v
```

### Python
Version 3.x

```bash
python --version
```

### Hardhat

```bash
npm install --save-dev hardhat
```

### PyQt5

```bash
pip install pyqt5 requests
```

### IPFS

Install IPFS Desktop or CLI:

https://docs.ipfs.tech/install/

Verify:

```bash
ipfs daemon
```

### SQLite

```bash
sqlite3 --version
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/medvault.git
cd medvault
```

### Install Backend Dependencies

```bash
cd Backend
npm install
```

### Install Python Dependencies

```bash
pip install pyqt5 requests
```

---

## 🚀 Running the Application

### 1. Start IPFS

```bash
ipfs daemon
```

### 2. Start Hardhat Network

```bash
npx hardhat node
```

### 3. Deploy Smart Contract

```bash
npx hardhat run scripts/deploy.js --network localhost
```

### 4. Start Backend

```bash
node index.mjs
```

### 5. Launch GUI

```bash
python main.py
```

---

## 👥 User Roles

### Admin

Can:
- Approve doctors
- Revoke doctors
- View all records
- Access audit logs
- Manage users

### Doctor

Can:
- Upload medical records
- View patient history
- Download files from IPFS
- Access personal dashboard

---

## 🔒 Security Features

### Authentication
- Ethereum signature-based login
- Nonce challenge-response mechanism
- JWT authorization tokens

### Data Protection
- AES encryption for sensitive files
- Encrypted private key storage
- No plaintext credentials

### Blockchain Security
- Immutable transaction logs
- On-chain role verification
- Tamper-resistant record history

### Storage Security
- IPFS content addressing
- CID integrity verification
- Distributed file storage

---

## 📁 Project Structure

```text
MedVault/
│
├── Backend/
│   ├── index.mjs
│   ├── routes/
│   ├── contracts/
│   └── utils/
│
├── contracts/
│   └── MedVault.sol
│
├── scripts/
│   └── deploy.js
│
├── login_gui.py
├── main_menu.py
├── upload_gui.py
├── record_viewer.py
├── doctor_dashboard.py
├── download_gui.py
│
├── medvault.db
│
└── README.md
```

---

## 📡 Main API Endpoints

### Authentication

```http
POST /auth/staff-verify
```

### Upload Record

```http
POST /upload
```

### Get Patient Records

```http
GET /records/:patientAddress
```

### Approve Doctor

```http
POST /approve-doctor
```

---

## 🔮 Future Improvements

- Ethereum Sepolia deployment
- Layer 2 support (Arbitrum / zkSync)
- PostgreSQL migration
- Mobile application
- WalletConnect integration
- Zero-Knowledge Proof access control
- IPFS pinning services (Pinata/Filecoin)

---

## 🎓 Academic Context

This project was developed as part of a Master's Dissertation:

**"A Blockchain-Based Cloud Solution for Hospital Patient Records"**

The system demonstrates how blockchain, IPFS, and cryptographic authentication can be integrated to improve the security, transparency, and auditability of healthcare data management.

---

## 📄 License

This project is intended for educational and research purposes.

---

## 👨‍💻 Author

**Alexandru Ștefăniță**

Master Dissertation Project – 2025

---

## ⭐ Acknowledgements

Special thanks to the open-source communities behind:

- Ethereum
- Solidity
- Hardhat
- IPFS
- Express.js
- PyQt5
- SQLite
