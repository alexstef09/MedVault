from PyQt5 import QtWidgets, QtGui, QtCore
import requests
import os

class UploadWindow(QtWidgets.QWidget):
    def __init__(self, address, token):
        super().__init__()
        self.address = address
        self.token = token
        self.file_path = None

        self.setWindowTitle("Upload Medical Record")
        self.setFixedSize(520, 430)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(30, 30, 30, 30)

        label = QtWidgets.QLabel("Upload Patient Record to MedVault")
        label.setFont(QtGui.QFont("Segoe UI", 15, QtGui.QFont.Bold))
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        # File picker
        self.choose_btn = QtWidgets.QPushButton("📂 Choose File")
        self.choose_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.choose_btn.setStyleSheet("""
            QPushButton {
                background-color: #7289da;
                padding: 12px;
                font-size: 15px;
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5b6eae;
            }
        """)
        self.choose_btn.clicked.connect(self.select_file)
        layout.addWidget(self.choose_btn)

        self.file_label = QtWidgets.QLabel("")
        self.file_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        layout.addWidget(self.file_label)

        # Patient Name
        self.name_entry = QtWidgets.QLineEdit()
        self.name_entry.setPlaceholderText("Enter Patient Full Name")
        self.name_entry.setStyleSheet("background-color: #3c3f41; color: white; padding: 10px; font-size: 13px;")
        layout.addWidget(self.name_entry)

        # Patient ID
        self.id_entry = QtWidgets.QLineEdit()
        self.id_entry.setPlaceholderText("Enter Patient ID")
        self.id_entry.setStyleSheet("background-color: #3c3f41; color: white; padding: 10px; font-size: 13px;")
        layout.addWidget(self.id_entry)

        # Upload button
        self.upload_btn = QtWidgets.QPushButton("🚀 Upload Record")
        self.upload_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #43b581;
                padding: 12px;
                font-size: 15px;
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: #35996a;
            }
        """)
        self.upload_btn.clicked.connect(self.upload)
        layout.addWidget(self.upload_btn)

    def select_file(self):
        file_dialog = QtWidgets.QFileDialog()
        filepath, _ = file_dialog.getOpenFileName(self, "Choose a file", "", "All files (*.*)")
        if filepath:
            self.file_path = filepath
            self.file_label.setText(f"📄 {os.path.basename(filepath)}")

    def upload(self):
        name = self.name_entry.text().strip()
        pid = self.id_entry.text().strip()

        if not self.file_path:
            QtWidgets.QMessageBox.warning(self, "No File", "Please choose a file first.")
            return

        if not name or not pid:
            QtWidgets.QMessageBox.warning(self, "Missing Info", "Please enter both Patient Name and ID.")
            return

        try:
            with open(self.file_path, "rb") as f:
                files = {'record': f}
                data = {
                    'patientAddress': self.address,  
                    'patientName': name,
                    'patientID': pid
                }

                res = requests.post("http://localhost:3000/upload", headers={
                    "Authorization": f"Bearer {self.token}"
                }, files=files, data=data)

            if res.status_code == 200:
                data = res.json()
                QtWidgets.QMessageBox.information(
                    self, "✅ Upload Successful",
                    f"CID:\n{data['cid']}\n\nTxHash:\n{data['txHash']}"
                )
                self.name_entry.clear()
                self.id_entry.clear()
                self.file_label.setText("")
            else:
                raise Exception(res.json().get("error", "Upload failed"))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Upload Failed", f"❌ Error: {e}")

