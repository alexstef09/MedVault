from PyQt5 import QtWidgets, QtGui, QtCore
import requests

class DoctorApprovalWindow(QtWidgets.QWidget):
    def __init__(self, address, token):
        super().__init__()
        self.address = address
        self.token = token

        self.setWindowTitle("Doctor Approval Panel")
        self.setFixedSize(660, 500)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Doctor Ethereum Address:")
        title.setFont(QtGui.QFont("Segoe UI", 12))
        layout.addWidget(title)

        # Entry
        self.addr_entry = QtWidgets.QLineEdit()
        self.addr_entry.setStyleSheet("background-color: #3c3f41; color: white; padding: 8px; font-size: 13px;")
        layout.addWidget(self.addr_entry)

        # Approve button
        approve_btn = QtWidgets.QPushButton("✅ Approve Doctor")
        approve_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        approve_btn.setStyleSheet("""
            QPushButton {
                background-color: #7289da;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5b6eae;
            }
        """)
        approve_btn.clicked.connect(self.approve_doctor)
        layout.addWidget(approve_btn)

        layout.addSpacing(15)

        # Table label
        list_label = QtWidgets.QLabel("Previously Approved Doctors:")
        list_label.setFont(QtGui.QFont("Segoe UI", 12))
        layout.addWidget(list_label)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Doctor Address", "Approved At"])
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(32)

        # Even column stretch to avoid layout gap
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: white;
                gridline-color: #444;
                font-size: 13px;
                border: none;
                selection-background-color: #7289da;
                selection-color: white;
            }

            QHeaderView::section {
                background-color: #36393f;
                color: white;
                font-weight: bold;
                border: none;
                padding: 6px;
            }

            QTableWidget::item {
                padding: 6px;
                border: none;
            }

            QScrollBar:vertical, QScrollBar:horizontal {
                background: #2c2f33;
                width: 10px;
                height: 10px;
            }

            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #555;
                border-radius: 5px;
            }

            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                border: none;
            }

            QTableCornerButton::section {
                background-color: #1e1e1e;  /* Blend the top-left corner */
                border: none;
            }
        """)

        layout.addWidget(self.table)
        self.load_doctors()

    def load_doctors(self):
        try:
            res = requests.get("http://localhost:3000/doctors", headers={
                "Authorization": f"Bearer {self.token}"
            })

            if res.status_code != 200:
                raise Exception(res.json().get('error', 'Failed to fetch doctors'))

            doctors = res.json().get('doctors', [])
            self.table.setRowCount(len(doctors))

            for i, doc in enumerate(doctors):
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(doc['address']))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(doc['approvedAt']))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not load doctor list:\n{e}")

    def approve_doctor(self):
        address = self.addr_entry.text().strip()
        if not address:
            QtWidgets.QMessageBox.warning(self, "Input Required", "Please enter a wallet address.")
            return

        try:
            res = requests.post("http://localhost:3000/approve-doctor", json={
                "doctorAddress": address
            }, headers={"Authorization": f"Bearer {self.token}"})

            if res.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", f"✅ Doctor approved: {address}")
                self.addr_entry.clear()
                self.load_doctors()
            else:
                raise Exception(res.json().get("error", "Approval failed"))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Approval Failed", f"❌ Error: {e}")
