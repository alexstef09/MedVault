import sys
import requests
from PyQt5 import QtWidgets, QtGui, QtCore
from eth_account import Account
from eth_account.messages import encode_defunct
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

class MedVaultLogin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MedVault Login")
        self.setFixedSize(600, 550)
        self.setStyleSheet("background-color: #2c2f33; color: white;")

        self.jwt_token = None
        self.address = None

        self.stack = QtWidgets.QStackedLayout()
        self.setLayout(self.stack)

        self.init_main_menu()
        self.init_admin_login()
        self.init_staff_login()

        self.stack.setCurrentIndex(0)

    def init_main_menu(self):
    
        menu = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(menu)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # Title with real shadow effect
        title = QtWidgets.QLabel("Welcome to MedVault")
        title_font = QtGui.QFont("Segoe UI", 26, QtGui.QFont.Bold)
        title_font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1.5)
        title.setFont(title_font)
        title.setAlignment(QtCore.Qt.AlignCenter)

        shadow = QGraphicsDropShadowEffect()
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 1)
        shadow.setColor(QtGui.QColor(0, 0, 0, 120))

        layout.addWidget(title)
        layout.addSpacing(10)

        # Subtitle
        subtitle = QtWidgets.QLabel("Select Login Type")
        subtitle_font = QtGui.QFont("Segoe UI", 16, QtGui.QFont.Medium)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #cccccc;
                padding-bottom: 10px;
            }
        """)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        # Buttons
        admin_btn = QtWidgets.QPushButton("🛡️ Admin Login")
        staff_btn = QtWidgets.QPushButton("👨‍⚕️ Staff Login")
        for btn in (admin_btn, staff_btn):
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.setMinimumHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #7289da;
                    padding: 12px;
                    font-size: 16px;
                    color: white;
                    border-radius: 8px;
                    margin: 10px 80px;
                }
                QPushButton:hover {
                    background-color: #5b6eae;
                }
            """)
            layout.addWidget(btn)

        admin_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        staff_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        self.stack.addWidget(menu)


    def init_admin_login(self):
        admin = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(admin)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        label = QtWidgets.QLabel("Admin Private Key:")
        label.setFont(QtGui.QFont("Segoe UI", 14))
        layout.addWidget(label)

        self.admin_entry = QtWidgets.QLineEdit()
        self.admin_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        self.admin_entry.setMinimumHeight(35)
        self.admin_entry.setFont(QtGui.QFont("Segoe UI", 12))
        layout.addWidget(self.admin_entry)

        layout.addSpacing(20)

        login_btn = QtWidgets.QPushButton("🔐 Login as Admin")
        back_btn = QtWidgets.QPushButton("⬅️ Back")

        for btn in (login_btn, back_btn):
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #7289da;
                    padding: 10px;
                    font-size: 14px;
                    color: white;
                    border-radius: 6px;
                    margin: 5px 60px;
                }
                QPushButton:hover {
                    background-color: #5b6eae;
                }
            """)
            layout.addWidget(btn)

        login_btn.clicked.connect(self.admin_login)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.stack.addWidget(admin)

    def init_staff_login(self):
        staff = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(staff)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        name_label = QtWidgets.QLabel("Your Name:")
        name_label.setFont(QtGui.QFont("Segoe UI", 14))
        layout.addWidget(name_label)

        self.name_entry = QtWidgets.QLineEdit()
        self.name_entry.setMinimumHeight(35)
        self.name_entry.setFont(QtGui.QFont("Segoe UI", 12))
        layout.addWidget(self.name_entry)

        layout.addSpacing(15)

        key_label = QtWidgets.QLabel("Private Key:")
        key_label.setFont(QtGui.QFont("Segoe UI", 14))
        layout.addWidget(key_label)

        self.staff_key_entry = QtWidgets.QLineEdit()
        self.staff_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        self.staff_key_entry.setMinimumHeight(35)
        self.staff_key_entry.setFont(QtGui.QFont("Segoe UI", 12))
        layout.addWidget(self.staff_key_entry)

        layout.addSpacing(20)

        login_btn = QtWidgets.QPushButton("👨‍⚕️ Login as Staff")
        back_btn = QtWidgets.QPushButton("⬅️ Back")

        for btn in (login_btn, back_btn):
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #7289da;
                    padding: 10px;
                    font-size: 14px;
                    color: white;
                    border-radius: 6px;
                    margin: 5px 60px;
                }
                QPushButton:hover {
                    background-color: #5b6eae;
                }
            """)
            layout.addWidget(btn)

        login_btn.clicked.connect(self.staff_login)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.stack.addWidget(staff)

    def admin_login(self):
        key = self.admin_entry.text().strip()
        try:
            acct = Account.from_key(key)
            self.address = acct.address
        except Exception:
            return QtWidgets.QMessageBox.critical(self, "Error", "Invalid private key.")

        try:
            r = requests.get(f"http://localhost:3000/auth/challenge?address={self.address}")
            nonce = r.json()['nonce']
            message = encode_defunct(text=f"Sign this nonce to authenticate: {nonce}")
            signed = Account.sign_message(message, private_key=key)

            res = requests.post("http://localhost:3000/auth/verify", json={
                "address": self.address,
                "signature": signed.signature.hex()
            })

            if res.status_code == 200:
                self.jwt_token = res.json()['token']
                QtWidgets.QMessageBox.information(self, "Success", "✅ Logged in as Admin.")
                self.hide()
                self.launch_main_menu()
            else:
                raise Exception(res.json().get('error', 'Unknown error'))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Login Failed", str(e))

    def staff_login(self):
        name = self.name_entry.text().strip()
        key = self.staff_key_entry.text().strip()

        if not name or not key:
            return QtWidgets.QMessageBox.critical(self, "Error", "Both fields are required.")

        try:
            acct = Account.from_key(key)
            self.address = acct.address
        except Exception:
            return QtWidgets.QMessageBox.critical(self, "Error", "Invalid private key.")

        try:
            r = requests.get(f"http://localhost:3000/auth/challenge?address={self.address}")
            nonce = r.json()['nonce']
            message = encode_defunct(text=f"Sign this nonce to authenticate: {nonce}")
            signed = Account.sign_message(message, private_key=key)

            res = requests.post("http://localhost:3000/auth/staff-verify", json={
                "address": self.address,
                "name": name,
                "signature": signed.signature.hex(),
                "nonce": nonce
            })

            if res.status_code == 200:
                data = res.json()
                self.jwt_token = data['token']
                confirmed_name = data.get("name", name)
                QtWidgets.QMessageBox.information(self, "Success", f"✅ Logged in as {confirmed_name}.")
                self.hide()
                self.launch_main_menu(confirmed_name)
            else:
                raise Exception(res.json().get('error', 'Unknown error'))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Login Failed", str(e))

    def launch_main_menu(self, name=None):
        from main_menu import MainMenu
        self.main_menu = MainMenu(self.address, self.jwt_token, name)
        self.main_menu.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MedVaultLogin()
    window.show()
    sys.exit(app.exec_())
