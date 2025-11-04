from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFormLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
    QTabWidget, QGroupBox, QDialog, QDialogButtonBox, QComboBox
)
from PyQt5.QtCore import pyqtSignal, Qt

class AdminDashboardWidget(QWidget):
    """Admin Dashboard UI."""
    logout_requested = pyqtSignal()
    
    # Signals for DB actions
    approve_user = pyqtSignal(int)
    deny_user = pyqtSignal(int)
    create_admin = pyqtSignal(str, str, str)
    
    # --- NEW SIGNALS ---
    add_user = pyqtSignal(str, str, str, str) # name, phone, password, role
    remove_user = pyqtSignal(int) # user_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # --- Tab 1: Approve Registrations ---
        self.approve_tab = QWidget()
        approve_layout = QVBoxLayout(self.approve_tab)
        
        approve_label = QLabel("Pending User Registrations")
        approve_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.pending_table = self._create_table(["ID", "Full Name", "Phone", "Role", "Registered At"])
        
        approve_btn_layout = QHBoxLayout()
        self.approve_button = QPushButton("Approve Selected")
        self.deny_button = QPushButton("Deny Selected")
        approve_btn_layout.addWidget(self.approve_button)
        approve_btn_layout.addWidget(self.deny_button)
        
        approve_layout.addWidget(approve_label)
        approve_layout.addWidget(self.pending_table)
        approve_layout.addLayout(approve_btn_layout)
        
        # --- Tab 2: Create New Admin ---
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

        # --- NEW Tab 3: Manage All Users ---
        self.manage_users_tab = QWidget()
        manage_layout = QVBoxLayout(self.manage_users_tab)
        
        manage_label = QLabel("All Users")
        manage_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        headers = ["ID", "Full Name", "Phone", "Role", "Status", "Created At"]
        self.all_users_table = self._create_table(headers)
        
        manage_btn_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Add New User")
        self.remove_user_button = QPushButton("Remove Selected User")
        manage_btn_layout.addWidget(self.add_user_button)
        manage_btn_layout.addWidget(self.remove_user_button)
        
        manage_layout.addWidget(manage_label)
        manage_layout.addWidget(self.all_users_table)
        manage_layout.addLayout(manage_btn_layout)

        # --- Add all tabs ---
        self.tabs.addTab(self.approve_tab, "Approve Registrations")
        self.tabs.addTab(self.manage_users_tab, "Manage All Users")
        self.tabs.addTab(self.create_admin_tab, "Create Admin (Legacy)")

        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(100)
        
        layout.addWidget(self.tabs)
        layout.addWidget(self.logout_button, alignment=Qt.AlignRight)
        
        # Connect signals
        self.logout_button.clicked.connect(self.logout_requested.emit)
        self.approve_button.clicked.connect(self._emit_approve_signal)
        self.deny_button.clicked.connect(self._emit_deny_signal)
        self.create_admin_button.clicked.connect(self._emit_create_admin_signal)
        
        # Connect new signals
        self.add_user_button.clicked.connect(self._show_add_user_dialog)
        self.remove_user_button.clicked.connect(self._emit_remove_user_signal)

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

    # --- NEW METHODS ---
    def _emit_remove_user_signal(self):
        user_id = self._get_selected_table_id(self.all_users_table)
        if user_id:
            confirm = QMessageBox.question(self, "Confirm Delete",
                "Are you sure you want to PERMANENTLY delete this user?\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.remove_user.emit(user_id)
    
    def _show_add_user_dialog(self):
        dialog = AddUserDialog(self)
        if dialog.exec_():
            name, phone, password, role = dialog.get_details()
            if not all([name, phone, password, role]):
                QMessageBox.warning(self, "Error", "All fields are required.")
                return
            self.add_user.emit(name, phone, password, role)

    # --- END NEW METHODS ---

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
    
    # --- NEW LOADER ---
    def load_all_users(self, users):
        """Populates the all users table."""
        self.all_users_table.setRowCount(0) # Clear table
        for row_num, user_data in enumerate(users):
            self.all_users_table.insertRow(row_num)
            # user_data = (id, full_name, phone, role, status)
            for col_num, data in enumerate(user_data):
                self.all_users_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
                
    def clear_admin_form(self):
        self.admin_name_input.clear()
        self.admin_phone_input.clear()
        self.admin_pass_input.clear()


# --- NEW DIALOG CLASS ---
class AddUserDialog(QDialog):
    """A dialog to add a new user."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_input = QComboBox()
        self.role_input.addItems(["admin", "doctor", "receptionist"])
        
        form_layout.addRow(QLabel("Full Name:"), self.name_input)
        form_layout.addRow(QLabel("Phone:"), self.phone_input)
        form_layout.addRow(QLabel("Password:"), self.password_input)
        form_layout.addRow(QLabel("Role:"), self.role_input)
        
        layout.addLayout(form_layout)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        layout.addWidget(self.buttons)

    def get_details(self):
        """Returns the details from the form."""
        return (
            self.name_input.text(),
            self.phone_input.text(),
            self.password_input.text(),
            self.role_input.currentText()
        )