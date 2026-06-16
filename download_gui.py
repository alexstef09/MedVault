from PyQt5 import QtWidgets, QtGui, QtCore
import requests
import cid
import os
import re

class DownloadWindow(QtWidgets.QDialog):
    def __init__(self, address, token, parent=None):
        super().__init__(parent)
        self.address = address
        self.token = token

        self.setWindowTitle("Download from IPFS")
        self.setFixedSize(600, 200)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Enter CID to download:")
        label.setFont(QtGui.QFont("Segoe UI", 12))
        layout.addWidget(label)

        self.cid_input = QtWidgets.QLineEdit()
        self.cid_input.setPlaceholderText("e.g., Qm...CID...")
        self.cid_input.setStyleSheet("padding: 10px; background-color: #3c3f41; border: 1px solid #555;")
        layout.addWidget(self.cid_input)

        self.download_btn = QtWidgets.QPushButton("⬇️ Download")
        self.download_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #43b581;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: #369c6a;
            }
        """)
        self.download_btn.clicked.connect(self.download_from_ipfs)
        layout.addWidget(self.download_btn)

    def download_from_ipfs(self):
        cid = self.cid_input.text().strip()
        if not cid:
            QtWidgets.QMessageBox.warning(self, "Missing CID", "Please enter a CID.")
            return

        try:
            url = f"http://localhost:8080/ipfs/{cid}"
            QtWidgets.QMessageBox.information(self, "Download Started", f"Opening:\n{url}")
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to download file:\n{e}")

    def normalize_cid(self, cid_string):
        cid_string = re.sub(r'[^\x21-\x7E]', '', cid_string)
        if cid_string.startswith("Qm") and len(cid_string) == 46:
            try:
                return cid.from_string(cid_string).to_v1().encode('base32')
            except Exception as e:
                raise ValueError(f"Invalid CID: {e}")
        return cid_string

    def download_file(self):
        cid_input = self.cid_entry.text().strip()
        if not cid_input:
            QtWidgets.QMessageBox.warning(self, "Input Required", "Please enter a valid IPFS CID.")
            return

        try:
            normalized_cid = self.normalize_cid(cid_input)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Invalid CID", f"❌ Error converting CID:\n{e}")
            return

        try:
            url = "http://127.0.0.1:5001/api/v0/cat"
            params = {'arg': normalized_cid}
            res = requests.post(url, params=params)

            if res.status_code != 200:
                raise Exception(f"Failed to fetch file: {res.status_code}")

            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", cid_input)
            if filename:
                with open(filename, "wb") as f:
                    f.write(res.content)
                QtWidgets.QMessageBox.information(self, "Success", f"✅ File saved as:\n{os.path.basename(filename)}")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Download Failed", f"❌ Error: {e}")
