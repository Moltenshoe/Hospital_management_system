from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
    QTabWidget
)
from PyQt5.QtCore import pyqtSignal, Qt

class DoctorDashboardWidget(QWidget):
    """Doctor Dashboard UI."""
    logout_requested = pyqtSignal()
    update_patient_status = pyqtSignal(int, str) # patient_id, status ("accepted" or "denied")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # --- Create Pending Tab ---
        self.pending_tab = QWidget()
        pending_layout = QVBoxLayout(self.pending_tab)
        
        pending_label = QLabel("Patients Awaiting Your Approval")
        pending_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        headers = ["ID", "Full Name", "Date of Birth", "Gender", "Contact Phone", "Problem", "Status", "Created At", "Blood Type"]
        self.pending_table = self._create_table(headers)
        
        pending_btn_layout = QHBoxLayout()
        self.accept_pending_button = QPushButton("Accept Selected")
        self.deny_pending_button = QPushButton("Deny Selected")
        pending_btn_layout.addWidget(self.accept_pending_button)
        pending_btn_layout.addWidget(self.deny_pending_button)
        
        pending_layout.addWidget(pending_label)
        pending_layout.addWidget(self.pending_table)
        pending_layout.addLayout(pending_btn_layout)
        
        # --- Create Accepted Tab ---
        self.accepted_tab = QWidget()
        accepted_layout = QVBoxLayout(self.accepted_tab)
        
        accepted_label = QLabel("Your Accepted Patients")
        accepted_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.accepted_table = self._create_table(headers)
        
        accepted_btn_layout = QHBoxLayout()
        # Per your request, we add "Accept" and "Deny" to both pages
        # "Accept" on this page will just re-accept them, having no effect
        # "Deny" will move them to 'denied' status
        self.accept_accepted_button = QPushButton("Accept Selected")
        self.deny_accepted_button = QPushButton("Deny Selected")
        accepted_btn_layout.addWidget(self.accept_accepted_button)
        accepted_btn_layout.addWidget(self.deny_accepted_button)
        
        accepted_layout.addWidget(accepted_label)
        accepted_layout.addWidget(self.accepted_table)
        accepted_layout.addLayout(accepted_btn_layout)

        # --- Add tabs ---
        self.tabs.addTab(self.pending_tab, "Pending Patients")
        self.tabs.addTab(self.accepted_tab, "Accepted Patients")
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(100)
        
        layout.addWidget(self.tabs)
        layout.addWidget(self.logout_button, alignment=Qt.AlignRight)

        # Connect signals
        self.logout_button.clicked.connect(self.logout_requested.emit)
        
        # Connect buttons for pending tab
        self.accept_pending_button.clicked.connect(lambda: self._emit_update_status("accepted", self.pending_table))
        self.deny_pending_button.clicked.connect(lambda: self._emit_update_status("denied", self.pending_table))
        
        # Connect buttons for accepted tab
        self.accept_accepted_button.clicked.connect(lambda: self._emit_update_status("accepted", self.accepted_table))
        self.deny_accepted_button.clicked.connect(lambda: self._emit_update_status("denied", self.accepted_table))

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

    def _emit_update_status(self, status, table_widget):
        """Helper to emit the update signal from the correct table."""
        patient_id = self._get_selected_patient_id(table_widget)
        if patient_id:
            # Check if status is already set
            current_status = table_widget.item(table_widget.currentRow(), 5).text()
            if current_status == status:
                QMessageBox.information(self, "Status", f"Patient is already {status}.")
                return
            self.update_patient_status.emit(patient_id, status)
            
    def _get_selected_patient_id(self, table_widget):
        """Gets the patient ID from the currently selected row of the given table."""
        selected_rows = table_widget.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient from the table.")
            return None
        selected_row = selected_rows[0].row()
        patient_id_item = table_widget.item(selected_row, 0)
        return int(patient_id_item.text())

    def load_assigned_patients(self, patients):
        """
        Populates both patient tables by sorting the full list of patients.
        """
        # Clear both tables
        self.pending_table.setRowCount(0)
        self.accepted_table.setRowCount(0)
        
        pending_row = 0
        accepted_row = 0
        
        for patient_data in patients:
            # patient_data = (id, full_name, age, gender, problem, doctor_status)
            status = patient_data[6]
            
            if status == 'pending':
                self.pending_table.insertRow(pending_row)
                for col_num, data in enumerate(patient_data):
                    self.pending_table.setItem(pending_row, col_num, QTableWidgetItem(str(data)))
                pending_row += 1
                
            elif status == 'accepted':
                self.accepted_table.insertRow(accepted_row)
                for col_num, data in enumerate(patient_data):
                    self.accepted_table.setItem(accepted_row, col_num, QTableWidgetItem(str(data)))
                accepted_row += 1
            
            # Patients with 'denied' status are not shown in either table