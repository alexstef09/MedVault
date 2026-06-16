// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MedVault {
    struct PatientRecord {
        string ipfsHash;      // IPFS hash of the patient's file
        address uploadedBy;   // Address of the uploader (doctor, hospital, etc.)
        uint256 timestamp;    // Time the record was uploaded
    }

    mapping(address => PatientRecord[]) public records; // Mapping of patient address => records

    mapping(address => bool) public isDoctor;           // Access control: doctors only
    address public admin;                               // The owner/admin of the contract

    event RecordUploaded(address indexed patient, string ipfsHash);
    event DoctorAdded(address doctor);
    event DoctorRemoved(address doctor);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    modifier onlyDoctor() {
        require(isDoctor[msg.sender], "Only approved doctors can upload");
        _;
    }

    constructor() {
        admin = msg.sender; // The deployer is the initial admin
    }

    function addDoctor(address _doctor) public onlyAdmin {
        isDoctor[_doctor] = true;
        emit DoctorAdded(_doctor);
    }

    function removeDoctor(address _doctor) public onlyAdmin {
        isDoctor[_doctor] = false;
        emit DoctorRemoved(_doctor);
    }

    function uploadRecord(address _patient, string memory _ipfsHash) public {
        require(isDoctor[msg.sender] || msg.sender == admin, "Only approved doctors or admin can upload");
        records[_patient].push(PatientRecord(_ipfsHash, msg.sender, block.timestamp));
        emit RecordUploaded(_patient, _ipfsHash);
    }


    function getRecordCount(address _patient) public view returns (uint256) {
        return records[_patient].length;
    }

    function getRecord(address _patient, uint256 index)
        public
        view
        returns (string memory, address, uint256)
    {
        PatientRecord memory record = records[_patient][index];
        return (record.ipfsHash, record.uploadedBy, record.timestamp);
    }
}
