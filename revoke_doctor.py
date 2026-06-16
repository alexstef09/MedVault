from PyQt5 import QtWidgets, QtGui, QtCore
import requests

class RevokeDoctorWindow(QtWidgets.QWidget):
    def __init__(self, address, token):
        super().__init__()
        self.address = address
        self.token = token

        self.setWindowTitle("Revoke Doctor Access")
        self.setFixedSize(800, 520)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QtWidgets.QLabel("Approved Doctors List:")
        title.setFont(QtGui.QFont("Segoe UI", 15, QtGui.QFont.Bold))
        layout.addWidget(title)

        # Table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Doctor Address", "Approved At"])
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
            QTableWidget::item:selected {
                background-color: #d9534f;
                color: white;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 500)
        self.table.setColumnWidth(1, 220)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        # Revoke Button
        self.revoke_btn = QtWidgets.QPushButton("🛑 Revoke Access")
        self.revoke_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.revoke_btn.setFixedHeight(42)
        self.revoke_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: #b0413e;
            }
        """)
        self.revoke_btn.clicked.connect(self.revoke_access)
        layout.addWidget(self.revoke_btn, alignment=QtCore.Qt.AlignCenter)

        self.load_doctors()

    def load_doctors(self):
        try:
            res = requests.get("http://localhost:3000/doctors", headers={
                "Authorization": f"Bearer {self.token}"
            })
            if res.status_code != 200:
                raise Exception(res.json().get("error", "Failed to fetch doctor list"))

            data = res.json().get("doctors", [])
            self.table.setRowCount(len(data))

            for row, doc in enumerate(data):
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(doc["address"]))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(doc["approvedAt"]))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Load Failed", f"Could not load doctors:\n{e}")

    def revoke_access(self):
        selected = self.table.currentRow()
        if selected < 0:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a doctor to revoke.")
            return

        doctor_address = self.table.item(selected, 0).text()

        try:
            res = requests.post("http://localhost:3000/revoke-doctor", json={
                "doctorAddress": doctor_address
            }, headers={ "Authorization": f"Bearer {self.token}" })

            if res.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Access Revoked", f"Doctor {doctor_address} was removed.")
                self.load_doctors()
            else:
                raise Exception(res.json().get("error", "Revocation failed"))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Revoke Failed", f"Error: {e}")
