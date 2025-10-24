# Hospital Management System (HMS) with PyQt5

Welcome! This is a simple, desktop-based Hospital Management System (HMS) built using Python, PyQt5 for the user interface, and SQLite for the database.

It's designed with three distinct user roles, each with their own permissions and dashboard.

<!-- Add a screenshot here! -->
![App Screenshot](/images/login_view.png)

## Features

* **Three User Roles:**
    * **Admin:** Can approve or deny new user registrations and create other admin accounts.
    * **Doctor:** Can view patients assigned to them and either "Accept" or "Deny" them.
    * **Receptionist:** Can create new patient records, delete patients, and assign patients to specific doctors.
* **Secure Login:** User passwords are "hashed" (encrypted) in the database and checked on login.
* **Registration System:** New doctors and receptionists can register, but their accounts must be approved by an admin before they can log in.
* **Live Data Refresh:** The application automatically polls the database every 5 seconds to refresh the data, ensuring multiple users see up-to-date information.

## How to Run

1.  **Clone or Download:**
    Get the code from this repository.
    ```bash
    git clone [https://github.com/Moltenshoe/Hospital_management_system.git](https://github.com/Moltenshoe/Hospital_management_system.git)
    cd Hospital_management_system
    ```

2.  **Install Requirements:**
    This project only requires `PyQt5`. You can install it using pip:
    ```bash
    pip install PyQt5
    ```

3.  **Run the App:**
    Execute the `main.py` file to start the application.
    ```bash
    python main.py
    ```
    The first time you run it, a new database file named `hms.db` will be created automatically in the same folder.

## Default Admin Login

A default admin account is created automatically when you first run the app.

* **Phone:** `admin`
* **Password:** `admin123`

You can use this account to log in and approve any new "doctor" or "receptionist" accounts you register.
