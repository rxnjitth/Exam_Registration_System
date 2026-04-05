# Exam Registration System

A Flask-based exam registration platform with separate student and admin areas. Students can browse exams, register for available slots, and download hall tickets as PDFs. Admins can create and manage exams, view registrations, and export registration data as CSV.

## Features

- User registration and login with role-based access control
- Student dashboard with upcoming exams and personal registrations
- Exam registration with seat tracking and deadline enforcement
- PDF hall ticket generation
- Admin dashboard with exam management
- CSV export for exam registrations
- Automated tests with `pytest`

## Tech Stack

- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- ReportLab
- pytest

## Project Structure

- `run.py` starts the application
- `config.py` holds app and test configuration
- `app/` contains the Flask package, models, routes, forms, templates, and utilities
- `tests/` contains the test suite

## Requirements

- Python 3.10+ recommended
- `pip`

## Setup

1. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application.

   ```bash
   python run.py
   ```

The app will create the database tables automatically on startup. By default, data is seeded with sample exams and an admin account.

## Default Admin Account

The seeded admin account is:

- Username: `admin`
- Email: `admin@example.com`
- Password: `admin12345`

Change these credentials before deploying the app anywhere public.

## Configuration

You can override the default settings with environment variables:

- `SECRET_KEY`
- `DATABASE_URL`

If `DATABASE_URL` is not set, the app uses a SQLite database at `instance/exam.db`.

## Running Tests

```bash
pytest
```

## Key Routes

- `/auth/register` and `/auth/login` for account access
- `/student/dashboard`, `/student/exams`, and `/student/registrations` for student actions
- `/admin/dashboard` and `/admin/exams` for admin management

## Notes

- The app uses CSRF protection in normal mode.
- Hall tickets are generated as PDF files.
- Exam registrations are protected by a unique student/exam constraint.