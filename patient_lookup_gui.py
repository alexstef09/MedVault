from PyQt5 import QtWidgets, QtGui, QtCore
import requests

class PatientLookupWindow(QtWidgets.QWidget):
    def __init__(self, address, token):
        super().__init__()
        self.address = address
        self.token = token

        self.setWindowTitle("Patient Lookup")
        self.setFixedSize(800, 520)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QtWidgets.QLabel("Enter patient name:")
        title.setFont(QtGui.QFont("Segoe UI", 14))
        layout.addWidget(title)

        self.entry = QtWidgets.QLineEdit()
        self.entry.setFont(QtGui.QFont("Segoe UI", 12))
        self.entry.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 13px;
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 6px;
                color: white;
            }
        """)
        layout.addWidget(self.entry)

        self.fetch_btn = QtWidgets.QPushButton("🔍 Lookup")
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

        # 🔍 Result display label
        self.result_label = QtWidgets.QLabel("")
        self.result_label.setFont(QtGui.QFont("Segoe UI", 12))
        self.result_label.setStyleSheet("color: lightgreen;")
        layout.addWidget(self.result_label)

        # Table (you can populate later if needed)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["IPFS CID", "Uploaded By", "Timestamp"])
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
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 380)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 180)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)
        self.fetch_btn.clicked.connect(self.lookup)

    def lookup(self):
        name = self.entry.text().strip()
        if not name:
            self.result_label.setText("⚠️ Please enter a patient full name.")
            return

        try:
            res = requests.get(f"http://localhost:3000/lookup/name/{name}", headers={
                "Authorization": f"Bearer {self.token}"
            })

            if res.status_code != 200:
                raise Exception(res.json().get("error", "Unknown error"))

            data = res.json()
            records = data.get("records", [])
            count = data.get("recordCount", 0)

            self.result_label.setText(f"📋 Records found for '{name}': {count}")
            self.table.setRowCount(len(records))

            for row, rec in enumerate(records):
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(rec['ipfsHash']))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(rec['uploadedBy']))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(rec['timestamp']))

        except Exception as e:
            self.result_label.setText(f"❌ Error: {str(e)}")

