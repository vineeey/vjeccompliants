# VJEC Complaints Management System

## Overview
This project is a comprehensive complaints management system for Vimal Jyothi Engineering College (VJEC). It allows students, staff, and administrators to submit, track, and resolve complaints efficiently. The system is built using Django and provides both web and API interfaces.

## Features
- **User Authentication**: Secure login/signup for students, staff, HODs, and Principal.
- **Complaint Submission**: Users can submit complaints with details, attachments, and priority.
- **Audio Complaint Submission**: Supports audio uploads and automatic transcription.
- **Department Routing**: Complaints are routed to relevant departments based on category or admin assignment.
- **Dashboard Views**:
  - Department Dashboard for HOD/Principal: Lists all complaints, with status and priority filters.
  - Individual Dashboard for users: Shows complaints submitted by the user.
- **Complaint Status Tracking**: Pending, In Review, Resolved statuses with history.
- **Priority Management**: Complaints can be marked as low, medium, or high priority.
- **Audit Trail**: Admin access and actions are logged for transparency.
- **Reports**: Generate and view reports on complaints and resolutions.
- **Role-Based Access**: Features and actions are shown/hidden based on user role (student, staff, HOD, Principal).
- **Offline Support**: Basic offline page for network issues.
- **REST API**: Endpoints for complaint creation, listing, detail, and status update.
- **Admin Panel**: Django admin for advanced management.

## Project Structure
- `complaints/` - Main app with models, views, templates, and management commands.
- `config/` - Django project configuration and settings.
- `static/` - Static files (CSS, JS, images).
- `templates/` - HTML templates for all pages.
- `media/` - Uploaded files and attachments.
- `requirements.txt` - Python dependencies.

## Screenshots
Below are screenshots demonstrating key features and UI:

![Dashboard](c:/Users/vinay/Pictures/Screenshots/Screenshot%20(45).png)
![Complaint Details](c:/Users/vinay/Pictures/Screenshots/Screenshot%20(62).png)
![Complaint Submission](c:/Users/vinay/Pictures/Screenshots/Screenshot%20(57).png)
![Admin Access](c:/Users/vinay/Pictures/Screenshots/Screenshot%20(55).png)
![Reports](c:/Users/vinay/Pictures/Screenshots/Screenshot%20(52).png)
![Audit Trail](c:/Users/vinay/Pictures/Screenshots/Screenshot%20(51).png)
![Complaint List](c:/Users/vinay/Pictures/Screenshots/Screenshot%20(49).png)
![Offline Page](c:/Users/vinay/Pictures/Screenshots/Screenshot%20(48).png)


## Admin Access (HOD/Principal)
To login as HOD or Principal, you will need the admin secret key:

**Admin Secret Key:** `adminisgoingtologin`

This key is used for the admin-access gate for HOD/Principal login. You can change it in your environment or in `config/settings.py`.

## Getting Started
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create a superuser: `python manage.py createsuperuser`
5. Start the server: `python manage.py runserver`
6. Access the app at `http://localhost:8000/`

## Usage
- Students and staff can submit complaints via the web interface.
- HODs and Principal can view, filter, and resolve complaints from the dashboard.
- Admins can manage users, departments, and audit logs via the admin panel.

## License
This project is for educational and internal use at VJEC.

---
For any issues or feature requests, contact the project maintainer.
