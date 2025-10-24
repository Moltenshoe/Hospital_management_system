from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QFormLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
    QTabWidget, QGroupBox, QDialog, QDialogButtonBox
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

# --- Admin Dashboard ---

class AdminDashboardWidget(QWidget):
    """Admin Dashboard UI."""
    logout_requested = pyqtSignal()
    
    # Signals for DB actions
    approve_user = pyqtSignal(int)
    deny_user = pyqtSignal(int)
    create_admin = pyqtSignal(str, str, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # Tab 1: Approve Registrations
        self.approve_tab = QWidget()
        approve_layout = QVBoxLayout(self.approve_tab)
        
        approve_label = QLabel("Pending User Registrations")
        approve_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.pending_table = self._create_table(["ID", "Full Name", "Phone", "Role"])
        
        approve_btn_layout = QHBoxLayout()
        self.approve_button = QPushButton("Approve Selected")
        self.deny_button = QPushButton("Deny Selected")
        approve_btn_layout.addWidget(self.approve_button)
        approve_btn_layout.addWidget(self.deny_button)
        
        approve_layout.addWidget(approve_label)
        approve_layout.addWidget(self.pending_table)
        approve_layout.addLayout(approve_btn_layout)
        
        # Tab 2: Create New Admin
        self.create_admin_tab = QWidget()
        admin_layout = QVBoxLayout(self.create_admin_tab)
        admin_layout.setAlignment(Qt.AlignTop)
        
        admin_box = QGroupBox("Create New Admin User")
        admin_box.setFixedWidth(350)
        admin_form = QFormLayout()
        self.admin_name_input = QLineEdit()
        self.admin_phone_input = QLineEdit()
        self.admin_pass_input = QLineEdit()
        self.admin_pass_input.setEchoMode(QLineEdit.Password)
        admin_form.addRow(QLabel("Full Name:"), self.admin_name_input)
        admin_form.addRow(QLabel("Phone:"), self.admin_phone_input)
        admin_form.addRow(QLabel("Password:"), self.admin_pass_input)
        self.create_admin_button = QPushButton("Create Admin")
        admin_form.addRow(self.create_admin_button)
        admin_box.setLayout(admin_form)
        admin_layout.addWidget(admin_box)

        self.tabs.addTab(self.approve_tab, "Approve Registrations")
        self.tabs.addTab(self.create_admin_tab, "Create Admin")

        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(100)
        
        layout.addWidget(self.tabs)
        layout.addWidget(self.logout_button, alignment=Qt.AlignRight)
        
        # Connect signals
        self.logout_button.clicked.connect(self.logout_requested.emit)
        self.approve_button.clicked.connect(self._emit_approve_signal)
        self.deny_button.clicked.connect(self._emit_deny_signal)
        self.create_admin_button.clicked.connect(self._emit_create_admin_signal)

    def _create_table(self, headers):
        """Helper to create a standard table widget."""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return table
        
    def _emit_approve_signal(self):
        user_id = self._get_selected_table_id(self.pending_table)
        if user_id:
            self.approve_user.emit(user_id)

    def _emit_deny_signal(self):
        user_id = self._get_selected_table_id(self.pending_table)
        if user_id:
            self.deny_user.emit(user_id)
            
    def _emit_create_admin_signal(self):
        self.create_admin.emit(
            self.admin_name_input.text(),
            self.admin_phone_input.text(),
            self.admin_pass_input.text()
        )

    def _get_selected_table_id(self, table):
        """Gets the ID (stored in column 0) of the selected row."""
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a user from the table.")
            return None
        selected_row = selected_rows[0].row()
        # ID is in the first column (index 0)
        user_id_item = table.item(selected_row, 0)
        return int(user_id_item.text())

    def load_pending_registrations(self, users):
        """Populates the pending users table."""
        self.pending_table.setRowCount(0) # Clear table
        for row_num, user_data in enumerate(users):
            self.pending_table.insertRow(row_num)
            # user_data = (id, full_name, phone, role)
            for col_num, data in enumerate(user_data):
                self.pending_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
                
    def clear_admin_form(self):
        self.admin_name_input.clear()
        self.admin_phone_input.clear()
        self.admin_pass_input.clear()

# --- Doctor Dashboard ---

class DoctorDashboardWidget(QWidget):
    """Doctor Dashboard UI."""
    logout_requested = pyqtSignal()
    update_patient_status = pyqtSignal(int, str) # patient_id, status ("accepted" or "denied")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("Your Assigned Patients")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Create table
        headers = ["ID", "Full Name", "Age", "Gender", "Problem", "Status"]
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(len(headers))
        self.patient_table.setHorizontalHeaderLabels(headers)
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.patient_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.patient_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.patient_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.accept_button = QPushButton("Accept Selected Patient")
        self.deny_button = QPushButton("Deny Selected Patient")
        btn_layout.addWidget(self.accept_button)
        btn_layout.addWidget(self.deny_button)
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(100)
        
        layout.addWidget(label)
        layout.addWidget(self.patient_table)
        layout.addLayout(btn_layout)
        layout.addStretch() # Pushes logout button to bottom
        layout.addWidget(self.logout_button, alignment=Qt.AlignRight)

        # Connect signals
        self.logout_button.clicked.connect(self.logout_requested.emit)
        self.accept_button.clicked.connect(lambda: self._emit_update_status("accepted"))
        self.deny_button.clicked.connect(lambda: self._emit_update_status("denied"))
        
    def _emit_update_status(self, status):
        patient_id = self._get_selected_patient_id()
        if patient_id:
            # Check if status is already set
            current_status = self.patient_table.item(self.patient_table.currentRow(), 5).text()
            if current_status == status:
                QMessageBox.information(self, "Status", f"Patient is already {status}.")
                return
            self.update_patient_status.emit(patient_id, status)
            
    def _get_selected_patient_id(self):
        selected_rows = self.patient_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient from the table.")
            return None
        selected_row = selected_rows[0].row()
        patient_id_item = self.patient_table.item(selected_row, 0)
        return int(patient_id_item.text())

    def load_assigned_patients(self, patients):
        """Populates the patient table."""
        self.patient_table.setRowCount(0) # Clear table
        for row_num, patient_data in enumerate(patients):
            self.patient_table.insertRow(row_num)
            # patient_data = (id, full_name, age, gender, problem, doctor_status)
            for col_num, data in enumerate(patient_data):
                self.patient_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

# --- Receptionist Dashboard ---

class ReceptionistDashboardWidget(QWidget):
    """Receptionist Dashboard UI."""
    logout_requested = pyqtSignal()
    create_patient = pyqtSignal(str, str, str, str) # name, age, gender, problem
    delete_patient = pyqtSignal(int) # patient_id
    assign_patient = pyqtSignal(int, int) # patient_id, doctor_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctors_list = [] # To store (id, name) tuples
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # Tab 1: Create Patient
        self.create_patient_tab = QWidget()
        patient_layout = QVBoxLayout(self.create_patient_tab)
        patient_layout.setAlignment(Qt.AlignTop)
        
        patient_box = QGroupBox("Create New Patient")
        patient_box.setFixedWidth(350)
        patient_form = QFormLayout()
        self.patient_name_input = QLineEdit()
        self.patient_age_input = QLineEdit()
        self.patient_gender_input = QComboBox()
        self.patient_gender_input.addItems(["Male", "Female", "Other"])
        self.patient_problem_input = QLineEdit()
        
        patient_form.addRow(QLabel("Full Name:"), self.patient_name_input)
        patient_form.addRow(QLabel("Age:"), self.patient_age_input)
        patient_form.addRow(QLabel("Gender:"), self.patient_gender_input)
        patient_form.addRow(QLabel("Problem:"), self.patient_problem_input)
        
        self.create_patient_button = QPushButton("Create Patient")
        patient_form.addRow(self.create_patient_button)
        patient_box.setLayout(patient_form)
        patient_layout.addWidget(patient_box)

        # Tab 2: Manage Patients
        self.manage_patients_tab = QWidget()
        manage_layout = QVBoxLayout(self.manage_patients_tab)
        manage_label = QLabel("All Patients")
        manage_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        headers = ["ID", "Full Name", "Age", "Problem", "Assigned Doctor", "Doctor Status"]
        self.all_patients_table = self._create_table(headers)
        
        manage_btn_layout = QHBoxLayout()
        self.assign_patient_button = QPushButton("Assign Selected Patient")
        self.delete_patient_button = QPushButton("Delete Selected Patient")
        manage_btn_layout.addWidget(self.assign_patient_button)
        manage_btn_layout.addWidget(self.delete_patient_button)
        
        manage_layout.addWidget(manage_label)
        manage_layout.addWidget(self.all_patients_table)
        manage_layout.addLayout(manage_btn_layout)

        self.tabs.addTab(self.create_patient_tab, "Create Patient")
        self.tabs.addTab(self.manage_patients_tab, "Manage Patients")

        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(100)
        
        layout.addWidget(self.tabs)
        layout.addWidget(self.logout_button, alignment=Qt.AlignRight)
        
        # Connect signals
        self.logout_button.clicked.connect(self.logout_requested.emit)
        self.create_patient_button.clicked.connect(self._emit_create_patient)
        self.delete_patient_button.clicked.connect(self._emit_delete_patient)
        self.assign_patient_button.clicked.connect(self._show_assign_dialog)
        
    def _create_table(self, headers):
        """Helper to create a standard table widget."""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return table
        
    def _emit_create_patient(self):
        self.create_patient.emit(
            self.patient_name_input.text(),
            self.patient_age_input.text(),
            self.patient_gender_input.currentText(),
            self.patient_problem_input.text()
        )
        
    def _get_selected_patient_id(self):
        selected_rows = self.all_patients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient from the table.")
            return None
        selected_row = selected_rows[0].row()
        patient_id_item = self.all_patients_table.item(selected_row, 0)
        return int(patient_id_item.text())
        
    def _emit_delete_patient(self):
        patient_id = self._get_selected_patient_id()
        if patient_id:
            # Confirmation dialog
            confirm = QMessageBox.question(self, "Confirm Delete",
                "Are you sure you want to delete this patient?",
                QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.delete_patient.emit(patient_id)

    def _show_assign_dialog(self):
        patient_id = self._get_selected_patient_id()
        if not patient_id:
            return
            
        dialog = AssignDoctorDialog(self.doctors_list, self)
        if dialog.exec_():
            doctor_id = dialog.get_selected_doctor_id()
            if doctor_id:
                self.assign_patient.emit(patient_id, doctor_id)

    def load_all_patients(self, patients):
        """Populates the 'all patients' table."""
        self.all_patients_table.setRowCount(0) # Clear table
        for row_num, patient_data in enumerate(patients):
            self.all_patients_table.insertRow(row_num)
            # data = (id, name, age, problem, doctor_name, doctor_status)
            for col_num, data in enumerate(patient_data):
                # Handle None (for unassigned doctor)
                item_text = str(data) if data is not None else "N/A"
                self.all_patients_table.setItem(row_num, col_num, QTableWidgetItem(item_text))
                
    def set_doctors_list(self, doctors):
        # doctors is a list of (id, name) tuples
        self.doctors_list = doctors
        
    def clear_patient_form(self):
        self.patient_name_input.clear()
        self.patient_age_input.clear()
        self.patient_problem_input.clear()


class AssignDoctorDialog(QDialog):
    """A dialog to select a doctor from a list."""
    def __init__(self, doctors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Assign Doctor")
        self.doctors = doctors # List of (id, name)
        
        layout = QVBoxLayout(self)
        
        self.doctor_combo = QComboBox()
        for doc_id, doc_name in self.doctors:
            self.doctor_combo.addItem(doc_name, doc_id) # Store ID in item data
            
        layout.addWidget(QLabel("Select a doctor to assign:"))
        layout.addWidget(self.doctor_combo)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        layout.addWidget(self.buttons)

    def get_selected_doctor_id(self):
        """Returns the ID of the selected doctor."""
        return self.doctor_combo.currentData()