# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- (Future changes will go here)

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