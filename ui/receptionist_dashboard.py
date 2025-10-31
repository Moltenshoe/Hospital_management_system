from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QFormLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
    QTabWidget, QGroupBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import pyqtSignal, Qt

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