from PyQt5 import QtWidgets, QtGui, QtCore
import requests

class DoctorDashboardWindow(QtWidgets.QWidget):
    def __init__(self, address, token):
        super().__init__()
        self.address = address
        self.token = token

        self.setWindowTitle("Doctor Dashboard")
        self.setFixedSize(800, 500)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QtWidgets.QLabel("Your Patients & Records")
        title.setFont(QtGui.QFont("Segoe UI", 18, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Patient Address", "Record Count"])
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
                background-color: #7289da;
            }
        """)
        self.table.setColumnWidth(0, 520)
        self.table.setColumnWidth(1, 180)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        self.load_dashboard_data()

    def load_dashboard_data(self):
        try:
            res = requests.get("http://localhost:3000/doctor-dashboard", headers={
                "Authorization": f"Bearer {self.token}"
            })

            if res.status_code != 200:
                raise Exception(res.json().get('error', 'Failed to load dashboard data'))

            data = res.json().get('patients', [])
            self.table.setRowCount(len(data))

            for row, entry in enumerate(data):
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(entry['patient']))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(entry['recordCount'])))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not load dashboard data:\n{e}")
