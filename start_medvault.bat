@echo off
title MedVault Launcher
color 0A

:: Step 1: Start IPFS in new terminal
echo [1/5] Starting IPFS...
start "IPFS" cmd /k "cd /d F:\IPFS\KUBO\kubo && ipfs daemon"
timeout /t 4 >nul

:: Step 2: Start Hardhat node in new terminal and wait manually
echo [2/5] Starting Hardhat node...
start "Hardhat Node" cmd /k "cd /d F:\VS Code\Projects\MedVault && npx hardhat node"
timeout /t 7 >nul

:: Step 3: Deploy contracts (waits here)
echo [3/5] Deploying contracts...
cd /d "F:\VS Code\Projects\MedVault"
call npx hardhat run scripts/deploy.js --network localhost

:: Step 4: Start backend in a new terminal
echo [4/5] Starting backend...
start "Backend Server" cmd /k "cd /d F:\VS Code\Projects\MedVault\Backend && node index.mjs"
timeout /t 4 >nul

:: Step 5: Launch GUI app (.exe)
echo [5/5] Launching MedVault GUI...
cd /d "F:\VS Code\Projects\MedVault\dist"
start login_gui.exe

exit
