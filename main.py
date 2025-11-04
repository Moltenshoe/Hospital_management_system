import sys
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

# Import our custom classes
from db_manager import DatabaseManager

# --- NEW IMPORTS ---
# Instead of one import, we import from our new, separate files
from ui.auth_widgets import LoginWidget, RegisterWidget
from ui.admin_dashboard import AdminDashboardWidget
from ui.doctor_dashboard import DoctorDashboardWidget
from ui.receptionist_dashboard import ReceptionistDashboardWidget, EditPatientDialog
# --- END NEW IMPORTS ---


class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        self.current_user_id = None
        self.current_user_role = None

        self.setWindowTitle("Hospital Management System")
        self.setGeometry(100, 100, 800, 600)
        
        self.setWindowIcon(QIcon("logo.png"))

        # Central stacked widget to hold all "pages"
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # Initialize all pages
        self.login_widget = LoginWidget()
        self.register_widget = RegisterWidget()
        self.admin_dashboard = AdminDashboardWidget()
        self.doctor_dashboard = DoctorDashboardWidget()
        self.receptionist_dashboard = ReceptionistDashboardWidget()

        # Add pages to the stack
        self.stack.addWidget(self.login_widget)
        self.stack.addWidget(self.register_widget)
        self.stack.addWidget(self.admin_dashboard)
        self.stack.addWidget(self.doctor_dashboard)
        self.stack.addWidget(self.receptionist_dashboard)
        
        self.cached_pending_users = []
        self.cached_all_users = []
        self.cached_doctor_patients = []
        self.cached_all_patients = []
        self.cached_doctors_list = []

        # Setup refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(5000) # 5000 ms = 5 seconds
        self.refresh_timer.timeout.connect(self.refresh_data_views)

        # Connect signals and slots
        self._connect_login_signals()
        self._connect_register_signals()
        self._connect_admin_signals()
        self._connect_doctor_signals()
        self._connect_receptionist_signals()

        # Show the first page
        self.show_login_page()

    # --- Page Navigation ---
    def show_login_page(self):
        self.refresh_timer.stop() # Stop polling when logged out
        self.current_user_id = None
        self.current_user_role = None
        
        self.cached_pending_users = []
        self.cached_all_users = []
        self.cached_doctor_patients = []
        self.cached_all_patients = []
        self.cached_doctors_list = []
        
        self.login_widget.clear_fields()
        self.stack.setCurrentWidget(self.login_widget)
        self.resize(380, 250)
        self.center()

    def show_register_page(self):
        self.refresh_timer.stop() # Stop polling here too
        self.register_widget.clear_fields()
        self.stack.setCurrentWidget(self.register_widget)
        self.resize(380, 300)
        self.center()
        
    def show_dashboard(self, role, user_id):
        self.current_user_id = user_id
        self.current_user_role = role
        
        self.resize(800, 600)
        self.center()
        
        if role == 'admin':
            self.load_admin_data()
            self.stack.setCurrentWidget(self.admin_dashboard)
        elif role == 'doctor':
            self.load_doctor_data()
            self.stack.setCurrentWidget(self.doctor_dashboard)
        elif role == 'receptionist':
            self.load_receptionist_data()
            self.stack.setCurrentWidget(self.receptionist_dashboard)
            
        self.refresh_timer.start() # Start the refresh timer
            
    def center(self):
        """Center the window on the screen."""
        frame_geom = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame_geom.moveCenter(center_point)
        self.move(frame_geom.topLeft())

    # --- Method for Refreshing ---
    def refresh_data_views(self):
        """
        Called by QTimer every 5 seconds to refresh the data
        in the currently active dashboard.
        """
        # Check which widget is currently visible
        current_widget = self.stack.currentWidget()
        
        if current_widget == self.admin_dashboard:
            print("Auto-refreshing Admin data...")
            self.load_admin_data()
        elif current_widget == self.doctor_dashboard:
            print("Auto-refreshing Doctor data...")
            self.load_doctor_data()
        elif current_widget == self.receptionist_dashboard:
            print("Auto-refreshing Receptionist data...")
            self.load_receptionist_data()
        # If on login or register page, timer is stopped, so this won't run.

    # --- Signal Connections ---

    def _connect_login_signals(self):
        self.login_widget.login_button.clicked.connect(self.handle_login)
        self.login_widget.register_requested.connect(self.show_register_page)

    def _connect_register_signals(self):
        self.register_widget.registration_submitted.connect(self.handle_registration)
        self.register_widget.back_to_login.connect(self.show_login_page)
        
    def _connect_admin_signals(self):
        self.admin_dashboard.logout_requested.connect(self.show_login_page)
        self.admin_dashboard.approve_user.connect(self.handle_approve_user)
        self.admin_dashboard.deny_user.connect(self.handle_deny_user)
        self.admin_dashboard.create_admin.connect(self.handle_create_admin)
        
        # --- NEW ADMIN CONNECTIONS ---
        self.admin_dashboard.add_user.connect(self.handle_add_user)
        self.admin_dashboard.remove_user.connect(self.handle_remove_user)

    def _connect_doctor_signals(self):
        self.doctor_dashboard.logout_requested.connect(self.show_login_page)
        self.doctor_dashboard.update_patient_status.connect(self.handle_update_patient_status)
        
    def _connect_receptionist_signals(self):
        self.receptionist_dashboard.logout_requested.connect(self.show_login_page)
        self.receptionist_dashboard.create_patient.connect(self.handle_create_patient)
        self.receptionist_dashboard.edit_patient_requested.connect(self.handle_edit_patient_request)
        self.receptionist_dashboard.delete_patient.connect(self.handle_delete_patient)
        self.receptionist_dashboard.assign_patient.connect(self.handle_assign_patient)

    # --- Data Loading ---

    def load_admin_data(self):
        # This function now loads data for BOTH admin tables
        
        # 1. Load Pending Users
        pending_users = self.db.get_pending_registrations()
        if pending_users != self.cached_pending_users:
            print("...Refreshing pending users table.")
            self.admin_dashboard.load_pending_registrations(pending_users)
            self.cached_pending_users = pending_users
        
        # 2. Load All Users
        all_users = self.db.get_all_users()
        if all_users != self.cached_all_users:
            print("...Refreshing all users table.")
            self.admin_dashboard.load_all_users(all_users)
            self.cached_all_users = all_users
        
    def load_doctor_data(self):
        patients = self.db.get_patients_for_doctor(self.current_user_id)
        
        if patients != self.cached_doctor_patients:
            print("...Refreshing doctor patients table.")
            self.doctor_dashboard.load_assigned_patients(patients) # The UI will sort them
            self.cached_doctor_patients = patients

    def load_receptionist_data(self):
        # 1. Load All Patients
        patients = self.db.get_all_patients()
        if patients != self.cached_all_patients:
            print("...Refreshing all patients table.")
            self.receptionist_dashboard.load_all_patients(patients)
            self.cached_all_patients = patients
            
        # 2. Load Doctors List
        doctors = self.db.get_doctors()
        if doctors != self.cached_doctors_list:
            print("...Refreshing doctors list.")
            self.receptionist_dashboard.set_doctors_list(doctors)
            self.cached_doctors_list = doctors

    # --- Logic Handlers ---

    def handle_login(self):
        phone = self.login_widget.phone_input.text()
        password = self.login_widget.password_input.text()
        
        if not phone or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both phone and password.")
            return
            
        role, user_id = self.db.check_credentials(phone, password)
        
        if role and user_id:
            self.show_dashboard(role, user_id)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid credentials or account not active.")

    def handle_registration(self, full_name, phone, password, role):
        if not all([full_name, phone, password]):
            QMessageBox.warning(self, "Registration Failed", "Please fill in all fields.")
            return
            
        if not self.register_widget.passwords_match():
            QMessageBox.warning(self, "Registration Failed", "Passwords do not match.")
            return
            
        if self.db.register_user(full_name, phone, password, role):
            QMessageBox.information(self, "Registration Successful",
                "Your registration is pending approval from an administrator.")
            self.show_login_page()
        else:
            QMessageBox.warning(self, "Registration Failed",
                "This phone number is already in use. Please try another.")

    # --- Admin Handlers ---
    def handle_approve_user(self, user_id):
        if self.db.approve_registration(user_id):
            QMessageBox.information(self, "Success", "User has been approved.")
            self.load_admin_data() # Refresh all admin tables
        else:
            QMessageBox.warning(self, "Error", "Could not approve user.")

    def handle_deny_user(self, user_id):
        if self.db.deny_registration(user_id):
            QMessageBox.information(self, "Success", "User has been denied and removed.")
            self.load_admin_data() # Refresh all admin tables
        else:
            QMessageBox.warning(self, "Error", "Could not deny user.")
            
    def handle_create_admin(self, name, phone, password):
        if not all([name, phone, password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        
        if self.db.create_admin_user(name, phone, password):
            QMessageBox.information(self, "Success", "New admin user created successfully.")
            self.admin_dashboard.clear_admin_form()
            self.load_admin_data() # Refresh all admin tables
        else:
            QMessageBox.warning(self, "Error", "Could not create admin. Phone may already be in use.")
    
    # --- NEW ADMIN HANDLERS ---
    def handle_add_user(self, name, phone, password, role):
        if self.db.create_user_by_admin(name, phone, password, role):
            QMessageBox.information(self, "Success", f"New {role} user created successfully.")
            self.load_admin_data() # Refresh all admin tables
        else:
            QMessageBox.warning(self, "Error", f"Could not create user. Phone may already be in use.")
            
    def handle_remove_user(self, user_id):
        if user_id == self.current_user_id:
            QMessageBox.warning(self, "Error", "You cannot delete your own account.")
            return
            
        if self.db.delete_user_by_admin(user_id, self.current_user_id):
            QMessageBox.information(self, "Success", "User has been permanently deleted.")
            self.load_admin_data() # Refresh all admin tables
        else:
            QMessageBox.warning(self, "Error", "Could not delete user.")
            
    # --- Doctor Handlers ---
    def handle_update_patient_status(self, patient_id, status):
        if self.db.update_patient_status_by_doctor(patient_id, status):
            QMessageBox.information(self, "Success", f"Patient status updated to '{status}'.")
            self.load_doctor_data() # Refresh doctor's tables
        else:
            QMessageBox.warning(self, "Error", "Could not update patient status.")
            
    # --- Receptionist Handlers ---
    # --- Receptionist Handlers ---
    def handle_create_patient(self, first_name, last_name, dob, gender, contact_phone, problem, address, blood_type):
        # All validation is now done in the UI, so we can just call the database.
        
        if self.db.create_patient(first_name, last_name, dob, gender, contact_phone, problem, address, blood_type, self.current_user_id):
            QMessageBox.information(self, "Success", "Patient created successfully.")
            self.receptionist_dashboard.clear_patient_form()
            self.load_receptionist_data() # Refresh table
        else:
            QMessageBox.warning(self, "Error", "Could not create patient.")
            
    def handle_edit_patient_request(self, patient_id):
        """Handles the request to edit a patient."""
        
        # 1. Fetch current data
        current_data = self.db.get_patient_details(patient_id)
        if not current_data:
            QMessageBox.warning(self, "Error", "Could not find patient data.")
            return
            
        # 2. Open the edit dialog, pre-filled with data
        dialog = EditPatientDialog(current_data, self)
        
        # 3. If the dialog is saved (OK clicked)
        if dialog.exec_():
            # 4. Get the new, edited details
            (first, last, dob, gender, phone, prob, addr, blood) = dialog.get_details()
            
            # 5. Run validation (same as creating a patient)
            if not all([first, last, phone, prob]):
                QMessageBox.warning(self, "Error", "Please fill in at least First Name, Last Name, Contact Phone, and Problem.")
                return
            if not first.isalpha() or not last.isalpha():
                QMessageBox.warning(self, "Error", "First and Last Name must contain only alphabets.")
                return

            # 6. Call the database to update
            if self.db.update_patient(patient_id, first, last, dob, gender, phone, prob, addr, blood):
                QMessageBox.information(self, "Success", "Patient details updated successfully.")
                self.load_receptionist_data() # Refresh the table
            else:
                QMessageBox.warning(self, "Error", "Could not update patient details.")
            
    def handle_delete_patient(self, patient_id):
        if self.db.delete_patient(patient_id):
            QMessageBox.information(self, "Success", "Patient deleted successfully.")
            self.load_receptionist_data() # Refresh table
        else:
            QMessageBox.warning(self, "Error", "Could not delete patient.")

    def handle_assign_patient(self, patient_id, doctor_id):
        if self.db.assign_patient_to_doctor(patient_id, doctor_id):
            QMessageBox.information(self, "Success", "Patient assigned to doctor.")
            self.load_receptionist_data() # Refresh table
        else:
            QMessageBox.warning(self, "Error", "Could not assign patient.")


if __name__ == "__main__":
    
    try:
        # A unique string to identify our app
        myappid = 'hms.app.v1.0' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except AttributeError:
        # This will fail on non-Windows systems, which is fine
        pass
    
    app = QApplication(sys.argv)
    
    # Initialize database
    db = DatabaseManager()
    
    # Pass the database manager to the main window
    main_window = MainWindow(db)
    main_window.show()
    
    sys.exit(app.exec_())