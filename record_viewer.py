from PyQt5 import QtWidgets, QtGui, QtCore
import requests

class RecordViewerWindow(QtWidgets.QWidget):
    def __init__(self, address, token):
        super().__init__()
        self.address = address
        self.token = token

        self.setWindowTitle("View Patient Records")
        self.setFixedSize(1000, 600)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QtWidgets.QLabel("Doctor/Admin Wallet Address:")
        title.setFont(QtGui.QFont("Segoe UI", 14))
        layout.addWidget(title)

        self.addr_entry = QtWidgets.QLineEdit()
        self.addr_entry.setText(address)
        self.addr_entry.setFont(QtGui.QFont("Segoe UI", 12))
        self.addr_entry.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 13px;
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 6px;
                color: white;
            }
        """)
        layout.addWidget(self.addr_entry)

        self.fetch_btn = QtWidgets.QPushButton("🔍 Fetch Records")
        self.fetch_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fetch_btn.setStyleSheet("""
            QPushButton {
                background-color: #7289da;
                padding: 12px;
                font-size: 15px;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5b6eae;
            }
        """)
        layout.addWidget(self.fetch_btn)

        self.count_label = QtWidgets.QLabel("")
        self.count_label.setFont(QtGui.QFont("Segoe UI", 12))
        layout.addWidget(self.count_label)

        self.table = QtWidgets.QTableWidget()
        self.table.setFont(QtGui.QFont("Segoe UI", 11))
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #444;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #2e2e2e;
                color: white;
                gridline-color: #555;
            }
        """)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.fetch_btn.clicked.connect(self.fetch_records)

    def fetch_records(self):
        wallet = self.addr_entry.text().strip()
        try:
            res = requests.get(f"http://localhost:3000/records/{wallet}", headers={
                "Authorization": f"Bearer {self.token}"
            })

            if res.status_code != 200:
                raise Exception(res.json().get('error', 'Unknown error'))

            data = res.json()
            records = data.get("records", [])
            count = data.get("count", 0)
            self.count_label.setText(f"Total Records: {count}")

            self.table.clearContents()
            self.table.setRowCount(0)

            if not records:
                self.table.setColumnCount(0)
                return

            is_admin_view = any("ipfsHash" in r for r in records)

            if is_admin_view:
                headers = ["Patient Name", "Patient ID", "CID", "Uploader", "Timestamp"]
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
                self.table.setRowCount(len(records))

                for row, rec in enumerate(records):
                    self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(rec.get("patientName", "") or "N/A"))
                    self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(rec.get("patientID", "") or "N/A"))
                    self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(rec.get("ipfsHash", "") or "N/A"))
                    self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(rec.get("uploadedBy", "") or "N/A"))
                    self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(rec.get("timestamp", "") or "N/A"))
            else:
                headers = ["Patient Name", "Patient ID", "Uploader Name"]
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
                self.table.setRowCount(len(records))

                for row, rec in enumerate(records):
                    self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(rec.get("patientName", "")))
                    self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(rec.get("patientID", "")))
                    self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(rec.get("uploaderName", "")))

                # 🧹 Clean table layout
                self.table.setColumnWidth(0, 300)  # Patient Name
                self.table.setColumnWidth(1, 200)  # Patient ID
                self.table.setColumnWidth(2, 300)  # Uploader Name
                self.table.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
                self.table.verticalHeader().setDefaultSectionSize(32)

            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Fetch Failed", f"Error: {e}")
