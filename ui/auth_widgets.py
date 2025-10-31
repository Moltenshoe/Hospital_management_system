from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QFormLayout, QGroupBox
)
from PyQt5.QtCore import pyqtSignal, Qt

class LoginWidget(QWidget):
    """Login Page UI."""
    # Signals: role, user_id
    login_successful = pyqtSignal(str, int) 
    register_requested = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow(QLabel("Phone:"), self.phone_input)
        form_layout.addRow(QLabel("Password:"), self.password_input)

        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)

        container = QGroupBox("Hospital Management System Login")
        container_layout = QVBoxLayout()
        container_layout.addLayout(form_layout)
        container_layout.addLayout(button_layout)
        container.setLayout(container_layout)
        container.setFixedWidth(350)

        layout.addWidget(container)
        
        # Connect internal signals
        self.register_button.clicked.connect(self.register_requested.emit)
        
    def clear_fields(self):
        self.phone_input.clear()
        self.password_input.clear()


class RegisterWidget(QWidget):
    """Registration Page UI."""
    registration_submitted = pyqtSignal(str, str, str, str)
    back_to_login = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.full_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.role_input = QComboBox()
        self.role_input.addItems(["doctor", "receptionist"])

        form_layout.addRow(QLabel("Full Name:"), self.full_name_input)
        form_layout.addRow(QLabel("Phone:"), self.phone_input)
        form_layout.addRow(QLabel("Password:"), self.password_input)
        form_layout.addRow(QLabel("Confirm Password:"), self.confirm_password_input)
        form_layout.addRow(QLabel("Role:"), self.role_input)

        self.submit_button = QPushButton("Submit Registration")
        self.back_button = QPushButton("Back to Login")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.back_button)

        container = QGroupBox("Register New User")
        container_layout = QVBoxLayout()
        container_layout.addLayout(form_layout)
        container_layout.addLayout(button_layout)
        container.setLayout(container_layout)
        container.setFixedWidth(350)
        
        layout.addWidget(container)

        # Connect internal signals
        self.back_button.clicked.connect(self.back_to_login.emit)
        self.submit_button.clicked.connect(self._handle_submit)

    def _handle_submit(self):
        """Emits signal with form data."""
        self.registration_submitted.emit(
            self.full_name_input.text(),
            self.phone_input.text(),
            self.password_input.text(),
            self.role_input.currentText()
        )

    def clear_fields(self):
        self.full_name_input.clear()
        self.phone_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        
    def passwords_match(self):
        return self.password_input.text() == self.confirm_password_input.text()