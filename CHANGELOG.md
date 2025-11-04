# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- (Future changes will go here)

---

## [0.3.0] - 2025-11-04
### Added
- **Admin:** Admins can now delete any existing user (except themselves).
- **Doctor:** Added an "Accept All Pending" button to the doctor's dashboard to accept all patients at once.
- **Receptionist:** Added an "Edit Selected Patient" button to the "Manage Patients" tab.
- **Receptionist:** Created a new `EditPatientDialog` popup that is pre-filled with the selected patient's data for editing.
- **Patient Form:** Added new fields to patient registration: `Date of Birth`, `Address`, `Blood Type`, and `Contact Phone`.
- **Patient Form:** The patient's `Age` is now automatically calculated and displayed based on their Date of Birth.
- **Timestamps:** Added `created_at` timestamp columns to both `users` and `patients` tables, which are automatically set on creation. This timestamp is now visible in all user/patient tables in the app.
- **Branding:** Added a custom application icon (`logo.png`) to the window's title bar and the Windows taskbar.

### Changed
- **Project Structure (Refactor):** The entire UI has been refactored for scalability. All classes from the single `ui_widgets.py` file have been split into a new `ui/` package with separate files:
    - `ui/auth_widgets.py`
    - `ui/admin_dashboard.py`
    - `ui/doctor_dashboard.py`
    - `ui/receptionist_dashboard.py`
- **Doctor:** The Doctor dashboard layout is now a `QTabWidget`, separating patients into a "Pending Patients" tab and an "Accepted Patients" tab.
- **Patient Form:** Changed `Full Name` field to separate `First Name` and `Last Name` fields.
- **Patient Form:** Added validation to `First Name` and `Last Name` to only allow alphabetic characters.
- **Patient Form:** Changed `Contact Phone` validation to require a 10-digit number.

### Fixed
- **Table Deselection Bug:** Implemented data caching in `main.py` to stop the 5-second auto-refresh from clearing the user's table selection. The table now only visually refreshes if the data has actually changed.
- **Doctor:** Fixed a bug where newly assigned patients were not appearing on the doctor's dashboard (was checking the wrong data column for "pending" status).
- **Receptionist:** Fixed a crash (`TypeError`) when clicking "Create Patient" with empty fields.
- **Receptionist:** Fixed a crash (`AttributeError`) related to `addYears` when setting the default date of birth.

---

## [0.2.0] - 2025-10-31
### Added
- **Admin:** Added a new "Manage All Users" tab to the admin dashboard.
- **Admin:** Admins can now create new, active users of any role (admin, doctor, receptionist) from their dashboard.
- **Admin:** Admins can now delete any existing user (except themselves).
- **Doctor:** Added an "Accept All Pending" button to the doctor's dashboard to accept all patients at once.

### Changed
- **Refactor:** The entire UI has been refactored for scalability. All classes from the single `ui_widgets.py` file have been split into a new `ui/` package with separate files:
    - `ui/auth_widgets.py`
    - `ui/admin_dashboard.py`
    - `ui/doctor_dashboard.py`
    - `ui/receptionist_dashboard.py`
- **Doctor:** The Doctor dashboard layout is now a `QTabWidget`, separating patients into a "Pending Patients" tab and an "Accepted Patients" tab.
- **Refactor:** `main.py` has been updated to import from the new `ui/` package.
- **Refactor:** `db_manager.py` was updated with new functions (`get_all_users`, `delete_user_by_admin`, `create_user_by_admin`, `accept_all_pending_patients`) to support the new features.

---

## [0.1.0] - 2025-10-24
### Added
- **Initial Project Release**
- **Core Structure:**
    - Created 3-file architecture (`main.py`, `db_manager.py`, `ui_widgets.py`).
    - Set up SQLite database (`hms.db`) for all data persistence.
    - Implemented `QStackedWidget` in `main.py` to manage all application pages.
- **Authentication:**
    - Secure login page (checks for "active" status).
    - User registration page (registers new users as "pending").
    - Password hashing using `hashlib` (SHA-256).
    - Auto-creation of a default admin (`admin`/`admin123`) on first run.
- **User Roles & Dashboards:**
    - **Admin:** Dashboard to view and approve/deny pending registrations. Added ability for admins to create new, active admin accounts.
    - **Doctor:** Dashboard to view all assigned patients. Added ability to "Accept" or "Deny" patients, which updates their status in the database.
    - **Receptionist:** Tabbed dashboard to (1) create new patient records, and (2) manage all patients, with options to delete or assign them to a doctor.
- **Features:**
    - Added a 5-second `QTimer` to auto-refresh all dashboard data, allowing for (near) real-time updates if multiple instances of the app are running.
- **Documentation:**
    - `README.md` with project description, features, and setup instructions.
    - `LICENSE` file (MIT License).
    - `.gitignore` to exclude the database and Python cache files from version control.
    