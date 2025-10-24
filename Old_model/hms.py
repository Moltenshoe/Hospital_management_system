import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ---------- Database Setup ----------
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        contact TEXT,
        address TEXT
    )
''')
conn.commit()

# ---------- Main Application ----------
class HospitalManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System")
        self.root.geometry("700x500")
        
        # --- Login Frame ---
        self.login_frame = tk.Frame(root)
        self.login_frame.pack(pady=50)
        
        tk.Label(self.login_frame, text="Admin Login", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(self.login_frame, text="Username:").grid(row=1, column=0, pady=5)
        tk.Label(self.login_frame, text="Password:").grid(row=2, column=0, pady=5)
        
        self.username_entry = tk.Entry(self.login_frame)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.username_entry.grid(row=1, column=1, pady=5)
        self.password_entry.grid(row=2, column=1, pady=5)
        
        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=3, column=0, columnspan=2, pady=10)
        
        # --- Main Frame (Hidden initially) ---
        self.main_frame = tk.Frame(root)
        self.toolbar = tk.Frame(self.main_frame)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(self.toolbar, text="Add Patient", command=self.add_patient).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Update Patient", command=self.update_patient).pack(side=tk.LEFT, padx=5)
        tk.Button(self.toolbar, text="Delete Patient", command=self.delete_patient).pack(side=tk.LEFT, padx=5)
        tk.Button(self.toolbar, text="Logout", command=self.logout).pack(side=tk.RIGHT, padx=5)
        
        # Patient Table
        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Name", "Age", "Gender", "Contact", "Address"), show='headings')
        for col in ("ID", "Name", "Age", "Gender", "Contact", "Address"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.load_patients()
    
    # ---------- Login ----------
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "admin" and password == "admin":  # hardcoded for simplicity
            self.login_frame.pack_forget()
            self.main_frame.pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    # ---------- Logout ----------
    def logout(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(pady=50)
    
    # ---------- Load Patients ----------
    def load_patients(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor.execute("SELECT * FROM patients")
        for patient in cursor.fetchall():
            self.tree.insert('', tk.END, values=patient)
    
    # ---------- Add Patient ----------
    def add_patient(self):
        self.patient_window("Add Patient")
    
    # ---------- Update Patient ----------
    def update_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a patient to update")
            return
        patient_id = self.tree.item(selected[0])['values'][0]
        self.patient_window("Update Patient", patient_id)
    
    # ---------- Delete Patient ----------
    def delete_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a patient to delete")
            return
        patient_id = self.tree.item(selected[0])['values'][0]
        cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
        conn.commit()
        self.load_patients()
    
    # ---------- Patient Form ----------
    def patient_window(self, title, patient_id=None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("400x300")
        
        tk.Label(win, text="Name").grid(row=0, column=0, pady=5)
        tk.Label(win, text="Age").grid(row=1, column=0, pady=5)
        tk.Label(win, text="Gender").grid(row=2, column=0, pady=5)
        tk.Label(win, text="Contact").grid(row=3, column=0, pady=5)
        tk.Label(win, text="Address").grid(row=4, column=0, pady=5)
        
        name_entry = tk.Entry(win)
        age_entry = tk.Entry(win)
        gender_entry = tk.Entry(win)
        contact_entry = tk.Entry(win)
        address_entry = tk.Entry(win)
        
        name_entry.grid(row=0, column=1, pady=5)
        age_entry.grid(row=1, column=1, pady=5)
        gender_entry.grid(row=2, column=1, pady=5)
        contact_entry.grid(row=3, column=1, pady=5)
        address_entry.grid(row=4, column=1, pady=5)
        
        if patient_id:
            cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
            patient = cursor.fetchone()
            name_entry.insert(0, patient[1])
            age_entry.insert(0, patient[2])
            gender_entry.insert(0, patient[3])
            contact_entry.insert(0, patient[4])
            address_entry.insert(0, patient[5])
        
        def save():
            name = name_entry.get()
            age = age_entry.get()
            gender = gender_entry.get()
            contact = contact_entry.get()
            address = address_entry.get()
            
            if patient_id:
                cursor.execute("""
                    UPDATE patients SET name=?, age=?, gender=?, contact=?, address=? WHERE id=?
                """, (name, age, gender, contact, address, patient_id))
            else:
                cursor.execute("""
                    INSERT INTO patients (name, age, gender, contact, address) VALUES (?, ?, ?, ?, ?)
                """, (name, age, gender, contact, address))
            conn.commit()
            self.load_patients()
            win.destroy()
        
        tk.Button(win, text="Save", command=save).grid(row=5, column=0, columnspan=2, pady=10)

# ---------- Run App ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalManagementApp(root)
    root.mainloop()
