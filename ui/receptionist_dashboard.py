from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QFormLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
    QTabWidget, QGroupBox, QDialog, QDialogButtonBox,
    QDateEdit, QTextEdit
)
from PyQt5.QtCore import pyqtSignal, Qt, QRegExp, QDate
from PyQt5.QtGui import QRegExpValidator
from datetime import datetime

class ReceptionistDashboardWidget(QWidget):
    """Receptionist Dashboard UI."""
    logout_requested = pyqtSignal()
    create_patient = pyqtSignal(str, str, str, str, str, str, str, str) # name, age, gender, contact_phone, problem
    delete_patient = pyqtSignal(int) # patient_id
    assign_patient = pyqtSignal(int, int) # patient_id, doctor_id
    edit_patient_requested = pyqtSignal(int) # patient_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctors_list = [] # To store (id, name) tuples
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # --- Tab 1: Create Patient ---
        self.create_patient_tab = QWidget()
        patient_layout = QVBoxLayout(self.create_patient_tab)
        patient_layout.setAlignment(Qt.AlignTop)
        
        patient_box = QGroupBox("Create New Patient")
        patient_box.setFixedWidth(400)
        patient_form = QFormLayout()

        # 1. First Name
        self.patient_first_name_input = QLineEdit()
        alpha_validator = QRegExpValidator(QRegExp("[a-zA-Z]+"))
        self.patient_first_name_input.setValidator(alpha_validator)
        patient_form.addRow(QLabel("First Name:"), self.patient_first_name_input)

        # 2. Last Name
        self.patient_last_name_input = QLineEdit()
        self.patient_last_name_input.setValidator(alpha_validator)
        patient_form.addRow(QLabel("Last Name:"), self.patient_last_name_input)

        # 3. Date of Birth
        self.patient_dob_input = QDateEdit()
        self.patient_dob_input.setCalendarPopup(True)
        self.patient_dob_input.setDisplayFormat("yyyy-MM-dd")
        self.patient_dob_input.setDate(QDate.currentDate().addYears(-18)) # Default to 18 years ago
        patient_form.addRow(QLabel("Date of Birth:"), self.patient_dob_input)

        # 4. Age (Auto-calculated)
        self.age_label = QLabel("Age: 18") # Initial value
        patient_form.addRow(self.age_label)
        self.patient_dob_input.dateChanged.connect(self._update_age_label) # Connect signal

        # 5. Gender
        self.patient_gender_input = QComboBox()
        self.patient_gender_input.addItems(["Male", "Female", "Other"])
        patient_form.addRow(QLabel("Gender:"), self.patient_gender_input)
        
        # --- ADD THIS NEW FIELD ---
        # 6. Contact Phone
        self.patient_phone_input = QLineEdit()
        # Validator for exactly 10 digits
        phone_validator = QRegExpValidator(QRegExp(r"\d{10}")) 
        self.patient_phone_input.setValidator(phone_validator)
        self.patient_phone_input.setMaxLength(10) # Physically limit to 10 chars
        self.patient_phone_input.setPlaceholderText("Enter 10-digit number")
        patient_form.addRow(QLabel("Contact Phone:"), self.patient_phone_input)

        # 6. Blood Type
        self.patient_blood_type_input = QComboBox()
        self.patient_blood_type_input.addItems(["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"])
        patient_form.addRow(QLabel("Blood Type:"), self.patient_blood_type_input)

        # 7. Address
        self.patient_address_input = QTextEdit()
        self.patient_address_input.setPlaceholderText("Enter patient's full address")
        self.patient_address_input.setFixedHeight(80)
        patient_form.addRow(QLabel("Address:"), self.patient_address_input)
        
        # 8. Problem
        self.patient_problem_input = QLineEdit()
        patient_form.addRow(QLabel("Problem:"), self.patient_problem_input)
        
        self.create_patient_button = QPushButton("Create Patient")
        patient_form.addRow(self.create_patient_button)
        patient_box.setLayout(patient_form)
        patient_layout.addWidget(patient_box)

        # --- Tab 2: Manage Patients ---
        self.manage_patients_tab = QWidget()
        manage_layout = QVBoxLayout(self.manage_patients_tab)
        manage_label = QLabel("All Patients")
        manage_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Update headers
        headers = ["ID", "Full Name", "Date of Birth", "Contact Phone", "Problem", "Assigned Doctor", "Doctor Status", "Created At", "Blood Type"]
        self.all_patients_table = self._create_table(headers)
        
        manage_btn_layout = QHBoxLayout()
        self.assign_patient_button = QPushButton("Assign Selected Patient")
        self.delete_patient_button = QPushButton("Delete Selected Patient")
        self.edit_patient_button = QPushButton("Edit Selected Patient")
        manage_btn_layout.addWidget(self.edit_patient_button)
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
        self.edit_patient_button.clicked.connect(self._emit_edit_request)
        
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
        # --- NEW VALIDATION ---
        first_name = self.patient_first_name_input.text()
        last_name = self.patient_last_name_input.text()
        contact_phone = self.patient_phone_input.text()
        problem = self.patient_problem_input.text()

        if not all([first_name, last_name, contact_phone, problem]):
            QMessageBox.warning(self, "Error", "Please fill in at least First Name, Last Name, Contact Phone, and Problem.")
            return # Stop here
            
        if not first_name.isalpha() or not last_name.isalpha():
            QMessageBox.warning(self, "Error", "First and Last Name must contain only alphabets.")
            return # Stop here
        # --- END VALIDATION ---

        # If validation passes, emit the signal
        self.create_patient.emit(
            first_name,
            last_name,
            self.patient_dob_input.date().toString("yyyy-MM-dd"),
            self.patient_gender_input.currentText(),
            contact_phone,
            problem,
            self.patient_address_input.toPlainText(),
            self.patient_blood_type_input.currentText()
        )
        
    def _emit_edit_request(self):
        """Gets the selected patient ID and emits a signal."""
        patient_id = self._get_selected_patient_id()
        if patient_id:
            self.edit_patient_requested.emit(patient_id)
        
    def _get_selected_patient_id(self):
        selected_rows = self.all_patients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient from the table.")
            return None
        selected_row = selected_rows[0].row()
        patient_id_item = self.all_patients_table.item(selected_row, 0)
        return int(patient_id_item.text())
    
    # --- ADD THIS NEW FUNCTION ---
    def _update_age_label(self):
        """Calculates and updates the age label based on the DOB input."""
        dob_qdate = self.patient_dob_input.date()
        dob = dob_qdate.toPyDate()
        today = datetime.now().date()
        
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        self.age_label.setText(f"Age: {age}")
    # --- END OF NEW FUNCTION ---
        
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
        self.patient_first_name_input.clear()
        self.patient_last_name_input.clear()
        self.patient_phone_input.clear() # --- ADD THIS ---
        self.patient_dob_input.setDate(QDate.currentDate().addYears(-18))
        self.patient_address_input.clear()
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
    
class EditPatientDialog(QDialog):
        def __init__(self, patient_data, parent=None):
            # patient_data is a tuple from get_patient_details
            super().__init__(parent)
            self.setWindowTitle("Edit Patient Details")

            # Unpack the data
            (first_name, last_name, dob, gender, contact_phone, 
            problem, address, blood_type) = patient_data

            layout = QVBoxLayout(self)
            patient_form = QFormLayout()

            # Create validators
            alpha_validator = QRegExpValidator(QRegExp("[a-zA-Z]+"))
            phone_validator = QRegExpValidator(QRegExp(r"\d{10}"))
            self.phone_input.setMaxLength(10) # Physically limit to 10 chars

            # 1. First Name
            self.first_name_input = QLineEdit()
            self.first_name_input.setValidator(alpha_validator)
            self.first_name_input.setText(first_name)
            patient_form.addRow(QLabel("First Name:"), self.first_name_input)

            # 2. Last Name
            self.last_name_input = QLineEdit()
            self.last_name_input.setValidator(alpha_validator)
            self.last_name_input.setText(last_name)
            patient_form.addRow(QLabel("Last Name:"), self.last_name_input)

            # 3. Date of Birth
            self.dob_input = QDateEdit()
            self.dob_input.setCalendarPopup(True)
            self.dob_input.setDisplayFormat("yyyy-MM-dd")
            self.dob_input.setDate(QDate.fromString(dob, "yyyy-MM-dd"))
            patient_form.addRow(QLabel("Date of Birth:"), self.dob_input)

            # 4. Gender
            self.gender_input = QComboBox()
            self.gender_input.addItems(["Male", "Female", "Other"])
            self.gender_input.setCurrentText(gender)
            patient_form.addRow(QLabel("Gender:"), self.gender_input)

            # 5. Contact Phone
            self.phone_input = QLineEdit()
            self.phone_input.setValidator(phone_validator)
            self.phone_input.setText(contact_phone)
            patient_form.addRow(QLabel("Contact Phone:"), self.phone_input)

            # 6. Blood Type
            self.blood_type_input = QComboBox()
            self.blood_type_input.addItems(["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"])
            self.blood_type_input.setCurrentText(blood_type)
            patient_form.addRow(QLabel("Blood Type:"), self.blood_type_input)

            # 7. Address
            self.address_input = QTextEdit()
            self.address_input.setPlainText(address)
            self.address_input.setFixedHeight(80)
            patient_form.addRow(QLabel("Address:"), self.address_input)
            
            # 8. Problem
            self.problem_input = QLineEdit()
            self.problem_input.setText(problem)
            patient_form.addRow(QLabel("Problem:"), self.problem_input)
            
            layout.addLayout(patient_form)

            # Dialog buttons
            self.buttons = QDialogButtonBox(
                QDialogButtonBox.Save | QDialogButtonBox.Cancel,
                Qt.Horizontal, self)
            self.buttons.accepted.connect(self.accept)
            self.buttons.rejected.connect(self.reject)
            layout.addWidget(self.buttons)

        def get_details(self):
            """Returns all the new values from the form fields."""
            return (
                self.first_name_input.text(),
                self.last_name_input.text(),
                self.dob_input.date().toString("yyyy-MM-dd"),
                self.gender_input.currentText(),
                self.phone_input.text(),
                self.problem_input.text(),
                self.address_input.toPlainText(),
                self.blood_type_input.currentText()
            )
    # --- END OF NEW CLASS ---