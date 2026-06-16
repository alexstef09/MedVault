async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contract with account:", deployer.address);

  const MedVault = await ethers.getContractFactory("MedVault");

  console.log("Deploying MedVault contract...");
  const medVault = await MedVault.deploy(); // Already awaited and mined

  console.log("Contract deployed successfully!");
  console.log("MedVault contract address:", medVault.target || medVault.address); // Hardhat v3 uses .target
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Deployment error:", error);
    process.exit(1);
  });
