from PyQt5 import QtWidgets, QtGui, QtCore
import requests

class UserManagementWindow(QtWidgets.QWidget):
    def __init__(self, address, token):
        super().__init__()
        self.address = address
        self.token = token

        self.setWindowTitle("User Management")
        self.setFixedSize(750, 560)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        layout = QtWidgets.QVBoxLayout(self)

        # ───── Section: Header ─────
        title = QtWidgets.QLabel("🧾 Register a New User")
        title.setFont(QtGui.QFont("Segoe UI", 15, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignLeft)
        title.setStyleSheet("margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(title)

        # ───── Section: Form ─────
        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.address_entry = QtWidgets.QLineEdit()
        self.name_entry = QtWidgets.QLineEdit()
        self.role_entry = QtWidgets.QComboBox()
        self.role_entry.addItems(["admin", "doctor", "staff"])

        input_style = "background-color: #3c3f41; color: white; padding: 8px; font-size: 13px;"

        for entry in [self.address_entry, self.name_entry, self.role_entry]:
            entry.setStyleSheet(input_style)

        form_layout.addRow("Address:", self.address_entry)
        form_layout.addRow("Name:", self.name_entry)
        form_layout.addRow("Role:", self.role_entry)

        layout.addLayout(form_layout)

        # ───── Section: Register Button ─────
        register_btn = QtWidgets.QPushButton("➕ Register / Update User")
        register_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #43b581;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 12px 80px 0 80px;
            }
            QPushButton:hover {
                background-color: #369c6a;
            }
        """)
        register_btn.clicked.connect(self.register_user)
        layout.addWidget(register_btn)

        layout.addSpacing(10)

        # ───── Section: Table Label ─────
        table_label = QtWidgets.QLabel("👥 Registered Users:")
        table_label.setFont(QtGui.QFont("Segoe UI", 13, QtGui.QFont.Bold))
        table_label.setAlignment(QtCore.Qt.AlignLeft)
        table_label.setStyleSheet("margin-top: 20px; margin-bottom: 5px;")
        layout.addWidget(table_label)

        # ───── Section: User Table ─────
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Address", "Name", "Role"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: white;
                gridline-color: #444;
                font-size: 12px;
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
                background-color: #1e1e1e;
                padding: 6px;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #7289da;
                color: white;
            }

            QScrollBar:vertical, QScrollBar:horizontal {
                background: #2c2f33;
                width: 10px;
                height: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #555;
                border-radius: 5px;
            }

            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                border: none;
            }
        """)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(False)
        layout.addWidget(self.table)

        self.load_users()

    def register_user(self):
        address = self.address_entry.text().strip()
        name = self.name_entry.text().strip()
        role = self.role_entry.currentText().strip()

        if not address or not name or not role:
            QtWidgets.QMessageBox.warning(self, "Missing Fields", "Please fill in all fields.")
            return

        try:
            res = requests.post("http://localhost:3000/users", json={
                "address": address,
                "name": name,
                "role": role
            }, headers={"Authorization": f"Bearer {self.token}"})

            if res.status_code != 200:
                raise Exception(res.json().get("error", "Registration failed"))

            QtWidgets.QMessageBox.information(self, "Success", "✅ User registered/updated successfully.")
            self.load_users()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def load_users(self):
        try:
            res = requests.get("http://localhost:3000/users", headers={"Authorization": f"Bearer {self.token}"})
            if res.status_code != 200:
                raise Exception(res.json().get("error", "Failed to fetch users"))

            users = res.json().get("users", [])
            self.table.setRowCount(len(users))

            for row, user in enumerate(users):
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(user['address']))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(user['name']))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(user['role']))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
