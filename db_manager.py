import sqlite3
import hashlib
import sys

class DatabaseManager:
    """
    This class handles all interactions with the SQLite database.
    """
    def __init__(self, db_name="hms.db"):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.create_tables()
            self._create_default_admin()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            sys.exit(1)

    def _hash_password(self, password):
        """Hashes a password for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_tables(self):
        """Creates the necessary tables if they don't exist."""
        try:
            # Users table: 'pending' status for new registrations, 'active' for approved
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                gender TEXT,
                contact_phone TEXT,
                problem TEXT,
                address TEXT,
                blood_type TEXT,
                assigned_doctor_id INTEGER,
                doctor_status TEXT DEFAULT 'pending',
                created_by_receptionist_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assigned_doctor_id) REFERENCES users (id),
                FOREIGN KEY (created_by_receptionist_id) REFERENCES users (id)
            );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def _create_default_admin(self):
        """Creates a default admin user if one doesn't exist."""
        try:
            self.cursor.execute("SELECT * FROM users WHERE role='admin' AND status='active'")
            if not self.cursor.fetchone():
                hashed_pass = self._hash_password("admin123")
                self.cursor.execute("""
                INSERT INTO users (full_name, phone, password, role, status)
                VALUES (?, ?, ?, ?, ?)
                """, ("Default Admin", "admin", hashed_pass, "admin", "active"))
                self.conn.commit()
                print("Default admin created. Phone: admin, Pass: admin123")
        except sqlite3.Error as e:
            print(f"Error creating default admin: {e}")

    def register_user(self, full_name, phone, password, role):
        """
        Registers a new user with 'pending' status.
        Returns True on success, False on failure (e.g., phone exists).
        """
        if role == "admin":
            return False # Admins can only be created by other admins
        try:
            hashed_pass = self._hash_password(password)
            self.cursor.execute("""
            INSERT INTO users (full_name, phone, password, role, status)
            VALUES (?, ?, ?, ?, 'pending')
            """, (full_name, phone, hashed_pass, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # This error occurs if the phone number is not unique
            return False
        except sqlite3.Error as e:
            print(f"Error registering user: {e}")
            return False

    def check_credentials(self, phone, password):
        """
        Checks if a user's phone and password are valid and 'active'.
        Returns (role, user_id) if successful, else (None, None).
        """
        try:
            hashed_pass = self._hash_password(password)
            self.cursor.execute("""
            SELECT role, id FROM users 
            WHERE phone = ? AND password = ? AND status = 'active'
            """, (phone, hashed_pass))
            result = self.cursor.fetchone()
            return result if result else (None, None)
        except sqlite3.Error as e:
            print(f"Error checking credentials: {e}")
            return (None, None)

    def get_pending_registrations(self):
        """Returns a list of all users with 'pending' status."""
        try:
            self.cursor.execute("SELECT id, full_name, phone, role, created_at FROM users WHERE status='pending'")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching pending registrations: {e}")
            return []

    def approve_registration(self, user_id):
        """Changes a user's status from 'pending' to 'active'."""
        try:
            self.cursor.execute("UPDATE users SET status='active' WHERE id=?", (user_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error approving registration: {e}")
            return False

    def deny_registration(self, user_id):
        """Deletes a 'pending' user."""
        try:
            self.cursor.execute("DELETE FROM users WHERE id=? AND status='pending'", (user_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error denying registration: {e}")
            return False
            
    def create_admin_user(self, full_name, phone, password):
        """Admin-only function to create a new, active admin user."""
        try:
            hashed_pass = self._hash_password(password)
            self.cursor.execute("""
            INSERT INTO users (full_name, phone, password, role, status)
            VALUES (?, ?, ?, 'admin', 'active')
            """, (full_name, phone, hashed_pass))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Phone already exists
        except sqlite3.Error as e:
            print(f"Error creating admin user: {e}")
            return False

    def get_doctors(self):
        """Returns a list of all active doctors (id, full_name)."""
        try:
            self.cursor.execute("SELECT id, full_name FROM users WHERE role='doctor' AND status='active'")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching doctors: {e}")
            return []

    def create_patient(self, first_name, last_name, dob, gender, contact_phone, problem, address, blood_type, receptionist_id):
        """Creates a new patient record."""
        try:
            self.cursor.execute("""
            INSERT INTO patients (first_name, last_name, date_of_birth, gender, contact_phone, problem, address, blood_type, created_by_receptionist_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (first_name, last_name, dob, gender, contact_phone, problem, address, blood_type, receptionist_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating patient: {e}")
            return False

    def delete_patient(self, patient_id):
        """Deletes a patient record."""
        try:
            self.cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting patient: {e}")
            return False

    def get_all_patients(self):
        """
        Returns a list of all patients with doctor's name if assigned.
        """
        try:
            # Use LEFT JOIN to include patients even if they have no doctor assigned
            self.cursor.execute("""
            SELECT p.id, p.first_name || ' ' || p.last_name, p.date_of_birth, p.contact_phone, p.problem, u.full_name, p.doctor_status, p.created_at, p.blood_type
            FROM patients p
            LEFT JOIN users u ON p.assigned_doctor_id = u.id
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching all patients: {e}")
            return []

    def assign_patient_to_doctor(self, patient_id, doctor_id):
        """Assigns a patient to a doctor and sets status to 'pending' for doctor."""
        try:
            self.cursor.execute("""
            UPDATE patients 
            SET assigned_doctor_id = ?, doctor_status = 'pending'
            WHERE id = ?
            """, (doctor_id, patient_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error assigning patient: {e}")
            return False

    def get_patients_for_doctor(self, doctor_id):
        """Returns all patients assigned to a specific doctor."""
        try:
            self.cursor.execute("""
            SELECT id, p.first_name || ' ' || p.last_name, date_of_birth, gender, contact_phone, problem, doctor_status, created_at, blood_type
            FROM patients p
            WHERE assigned_doctor_id = ?
            """, (doctor_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching patients for doctor: {e}")
            return []

    def update_patient_status_by_doctor(self, patient_id, new_status):
        """Allows a doctor to 'accept' or 'deny' a patient."""
        if new_status not in ('accepted', 'denied'):
            return False
        try:
            self.cursor.execute("""
            UPDATE patients 
            SET doctor_status = ?
            WHERE id = ?
            """, (new_status, patient_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating patient status: {e}")
            return False
        

    # --- NEW ADMIN FUNCTIONS ---

    def get_all_users(self):
        """Returns a list of all users."""
        try:
            self.cursor.execute("SELECT id, full_name, phone, role, status, created_at FROM users")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching all users: {e}")
            return []

    def delete_user_by_admin(self, user_id, admin_id):
        """Deletes any user. Prevents admin self-deletion."""
        if user_id == admin_id:
            print("Admin cannot delete themselves.")
            return False # Admin cannot delete themselves
        try:
            # Also delete patients created by this user if they are a receptionist
            # Or unassign patients if they are a doctor (optional, but good practice)
            
            # For simplicity, we just delete the user.
            # In a real app, you'd handle foreign key constraints.
            
            self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            return False

    def create_user_by_admin(self, full_name, phone, password, role):
        """Admin-only function to create a new, active user of any role."""
        if role not in ('admin', 'doctor', 'receptionist'):
            return False
        try:
            hashed_pass = self._hash_password(password)
            self.cursor.execute("""
            INSERT INTO users (full_name, phone, password, role, status)
            VALUES (?, ?, ?, ?, 'active')
            """, (full_name, phone, hashed_pass, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Phone already exists
        except sqlite3.Error as e:
            print(f"Error creating user by admin: {e}")
            return False
    
    # --- ADD THESE TWO NEW FUNCTIONS ---

    def get_patient_details(self, patient_id):
        """
        Fetches all editable details for a single patient.
        Returns a tuple of the data.
        """
        try:
            self.cursor.execute("""
            SELECT first_name, last_name, date_of_birth, gender, 
                   contact_phone, problem, address, blood_type
            FROM patients 
            WHERE id = ?
            """, (patient_id,))
            return self.cursor.fetchone() # Returns one tuple or None
        except sqlite3.Error as e:
            print(f"Error fetching patient details: {e}")
            return None

    def update_patient(self, patient_id, first_name, last_name, dob, gender, contact_phone, problem, address, blood_type):
        """Updates an existing patient's record."""
        try:
            self.cursor.execute("""
            UPDATE patients SET
                first_name = ?,
                last_name = ?,
                date_of_birth = ?,
                gender = ?,
                contact_phone = ?,
                problem = ?,
                address = ?,
                blood_type = ?
            WHERE id = ?
            """, (first_name, last_name, dob, gender, contact_phone, problem, address, blood_type, patient_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating patient: {e}")
            return False

    # --- END OF NEW FUNCTIONS ---
    
    def __del__(self):
        """Close the database connection when the object is destroyed."""
        if hasattr(self, 'conn'):
            self.conn.close()