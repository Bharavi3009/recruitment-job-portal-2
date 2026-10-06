# Recruitment and Job Application Portal

A complete Django + SQLite recruitment portal suitable for a college/project submission.

## Features
- Admin and candidate authentication
- Candidate registration
- Admin job CRUD
- Candidate job search and details
- CV upload (PDF/DOC/DOCX)
- Candidate application history and status
- Admin application management and status updates
- Dashboard statistics
- Responsive Bootstrap UI
- Validation and permission checks
- SQLite database
- Sample data/credentials

## Tech stack
- Python
- Django
- SQLite
- HTML/CSS
- Bootstrap 5 (CDN)

## Setup in VS Code

### 1. Extract/open the project
Open the `recruitment_portal` folder in VS Code.

### 2. Create a virtual environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create sample users and jobs
```bash
python manage.py seed_data
```

This creates:
- Admin: `admin`
- Admin password: `Admin@12345`
- Candidate: `candidate`
- Candidate password: `Candidate@12345`

Change these credentials before deployment/submission.

### 6. Start the server
```bash
python manage.py runserver
```

Open:
http://127.0.0.1:8000/

Admin panel:
http://127.0.0.1:8000/admin/

## Important CV upload note
Uploaded CVs are stored in `media/cvs/`. The folder is created automatically.

## Project structure
```text
recruitment_portal/
├── manage.py
├── requirements.txt
├── README.md
├── recruitment_portal/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── jobs/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── management/commands/seed_data.py
├── templates/
│   ├── base.html
│   ├── registration/
│   └── jobs/
├── static/css/style.css
└── media/cvs/
```

## How to explain the project
- `CandidateProfile` extends Django's User model using a OneToOne relationship.
- `Job` stores job openings created by admins.
- `Application` connects a candidate to a job using ForeignKeys.
- A unique constraint prevents the same candidate applying twice to the same job.
- Django decorators/mixins restrict admin-only operations.
- `ModelForm` handles validation and CV uploads.
- Dashboard uses Django ORM aggregation/counting for statistics.


## Added features (enhanced version)
- Advanced job search by keyword, location, category, job type and experience level.
- Candidate bookmarks/saved jobs.
- Editable candidate profile with skills, education and experience.
- Application tracking cards with status timeline and last-updated timestamp.
- Admin dashboard status bars and job/application counts.
- Password reset flow; for local development, reset links print in the VS Code terminal (console email backend). Configure real email SMTP before deployment.
- Browser-persisted light/dark theme toggle.

## Run after updating models
From the folder containing `manage.py`, activate your virtual environment and run:
```powershell
python -m pip install -r requirements.txt
python manage.py makemigrations jobs
python manage.py migrate
python manage.py check
python manage.py runserver
```
If you already have local edits, back up your project and database before copying these files over. Do not deploy with `DEBUG=True` or the demo secret key.
