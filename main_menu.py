from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox,
    QScrollArea, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import requests
import json
import os

from login_gui import MedVaultLogin
from upload_gui import UploadWindow
from record_viewer import RecordViewerWindow
from doctor_dashboard import DoctorDashboardWindow
from revoke_doctor import RevokeDoctorWindow
from download_gui import DownloadWindow
from user_management import UserManagementWindow
from doctor_approval import DoctorApprovalWindow
from patient_lookup_gui import PatientLookupWindow

ADMIN_ADDRESS = "0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199".lower()

class MainMenu(QWidget):
    def __init__(self, address, token, name=None):
        super().__init__()
        self.address = address
        self.token = token
        self.name = name

        self.setWindowTitle("MedVault Main Menu")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        layout = QVBoxLayout(self)

        header = QLabel("MedVault Dashboard")
        header.setFont(QFont("Segoe UI", 26, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        user_info = f"{name} ({address})" if name else address
        user_label = QLabel(f"Logged in as:\n{user_info}")
        user_label.setAlignment(Qt.AlignCenter)
        user_label.setFont(QFont("Segoe UI", 14))
        user_label.setStyleSheet("margin: 5px 0 15px 0;")
        layout.addWidget(user_label)

        def add_button(text, callback, color="#7289da"):
            button = QPushButton(text)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: none;
                    padding: 12px;
                    font-size: 16px;
                    border-radius: 6px;
                    color: white;
                    margin: 6px 100px;
                }}
                QPushButton:hover {{
                    background-color: {'#5b6eae' if color == '#7289da' else '#7a2222'};
                }}
            """)
            button.clicked.connect(callback)
            layout.addWidget(button)

        if self.address.lower() == ADMIN_ADDRESS:
            add_button("🧾 View Hardhat Accounts", self.show_hardhat_accounts)

        add_button("📤 Upload Record", self.upload)
        add_button("📁 View Records", self.view_records)
        add_button("🧬 Patient Lookup & History", self.open_patient_lookup)
        add_button("📋 Doctor Dashboard", self.doctor_dashboard)
        add_button("✖ Revoke Doctor Access", self.revoke_doctor)
        add_button("📥 Download from IPFS", self.download_ipfs)
        add_button("👥 Manage Users", self.manage_users)
        add_button("🧑‍💼 Approve Doctor", self.approve_doctor)
        add_button("🕵️‍♂️ Audit Log", self.view_audit_log)
        add_button("🔓 Logout", self.logout)
        add_button("❌ Exit", self.close, color="#992e2e")

    def upload(self):
        self.upload_win = UploadWindow(self.address, self.token)
        self.upload_win.show()

    def view_records(self):
        self.viewer = RecordViewerWindow(self.address, self.token)
        self.viewer.show()

    def doctor_dashboard(self):
        self.dashboard = DoctorDashboardWindow(self.address, self.token)
        self.dashboard.show()

    def revoke_doctor(self):
        self.revoke = RevokeDoctorWindow(self.address, self.token)
        self.revoke.show()

    def download_ipfs(self):
        self.downloader = DownloadWindow(self.address, self.token)
        self.downloader.exec_()

    def manage_users(self):
        if self.address.lower() != ADMIN_ADDRESS:
            QMessageBox.warning(self, "Access Denied", "Only the admin can manage users.")
            return

        self.users = UserManagementWindow(self.address, self.token)
        self.users.show()

    def open_patient_lookup(self):
        self.lookup_window = PatientLookupWindow(self.address, self.token)
        self.lookup_window.show()

    def approve_doctor(self):
        self.approval = DoctorApprovalWindow(self.address, self.token)
        self.approval.show()

    def logout(self):
        from main_menu import MainMenu
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.login_window = MedVaultLogin()
            self.login_window.show()
            self.close()

    def view_audit_log(self):
        if self.address.lower() != ADMIN_ADDRESS:
            QMessageBox.warning(self, "Access Denied", "Only the admin can view the audit log.")
            return

        try:
            res = requests.get("http://localhost:3000/audit-log", headers={
                "Authorization": f"Bearer {self.token}"
            })
            logs = res.json().get('log', [])

            self.audit_window = QWidget()
            self.audit_window.setWindowTitle("Audit Log")
            self.audit_window.resize(800, 500)
            self.audit_window.setStyleSheet("background-color: #2c2f33; color: white;")

            layout = QVBoxLayout(self.audit_window)

            header = QLabel("🕵️ Audit Log")
            header.setFont(QFont("Segoe UI", 18, QFont.Bold))
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("padding: 10px;")
            layout.addWidget(header)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("border: none;")

            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(20, 10, 20, 10)
            container_layout.setSpacing(15)

            for log in logs:
                frame = QFrame()
                frame.setStyleSheet("""
                    QFrame {
                        background-color: #1e1e1e;
                        border: 1px solid #444;
                        border-radius: 8px;
                        padding: 12px;
                    }
                """)
                frame_layout = QVBoxLayout(frame)

                accessor_label = QLabel(f"Accessor: {log['accessor']}")
                accessor_label.setFont(QFont("Consolas", 11))
                accessor_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

                patient_label = QLabel(f"Patient: {log['patient']}")
                patient_label.setFont(QFont("Consolas", 11))
                patient_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

                timestamp_label = QLabel(f"Time: {log['timestamp']}")
                timestamp_label.setFont(QFont("Consolas", 10))
                timestamp_label.setStyleSheet("color: #ccc;")
                timestamp_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

                frame_layout.addWidget(accessor_label)
                frame_layout.addWidget(patient_label)
                frame_layout.addWidget(timestamp_label)

                container_layout.addWidget(frame)

            container_layout.addStretch(1)
            scroll.setWidget(container)
            layout.addWidget(scroll)

            self.audit_window.setLayout(layout)
            self.audit_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_hardhat_accounts(self):
        try:
            import sys

            if getattr(sys, 'frozen', False):
                base_dir = sys._MEIPASS
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, "Backend", "hardhat_accounts.json")
            with open(path, "r") as file:
                data = json.load(file)

            res = requests.get("http://localhost:3000/users", headers={
                "Authorization": f"Bearer {self.token}"
            })
            users = res.json().get("users", [])

            self.accounts_window = QWidget()
            self.accounts_window.setWindowTitle("Hardhat Accounts")
            self.accounts_window.resize(900, 600)
            self.accounts_window.setStyleSheet("background-color: #2c2f33; color: white;")

            layout = QVBoxLayout(self.accounts_window)

            header = QLabel("Hardhat Accounts")
            header.setFont(QFont("Segoe UI", 20, QFont.Bold))
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("padding: 12px;")
            layout.addWidget(header)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("border: none;")

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(20, 10, 20, 10)
            content_layout.setSpacing(15)

            for acc in data:
                name = next((u["name"] for u in users if u["address"].lower() == acc["address"].lower()), "Unassigned")

                frame = QFrame()
                frame.setStyleSheet("""
                    QFrame {
                        background-color: #1e1e1e;
                        border: 1px solid #444;
                        border-radius: 8px;
                        padding: 12px;
                    }
                """)
                frame_layout = QVBoxLayout(frame)

                name_label = QLabel(f"{name} - {acc['address']}")
                name_label.setFont(QFont("Consolas", 11))
                name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

                key_label = QLabel(f"Private Key: {acc['privateKey']}")
                key_label.setFont(QFont("Consolas", 10))
                key_label.setStyleSheet("color: #bbbbbb;")
                key_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

                frame_layout.addWidget(name_label)
                frame_layout.addWidget(key_label)
                content_layout.addWidget(frame)

            content_layout.addStretch(1)
            scroll_area.setWidget(content_widget)
            layout.addWidget(scroll_area)

            self.accounts_window.setLayout(layout)
            self.accounts_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load accounts: {e}")