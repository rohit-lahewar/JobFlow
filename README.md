# JobFlow — Job Application & Interview Management System

A production-ready, full-stack Python web application designed to help job seekers, software engineers, and tech professionals track, organize, and accelerate their career pipeline.

JobFlow features complete authentication, strict multi-tenant data isolation, real-time KPI metrics, multi-field application search and filtering, multi-stage interview management, follow-up scheduling, notes with cascade lifecycle management, responsive Chart.js visual analytics, and a RESTful JSON API.

---

## 🚀 Project Overview

Searching for a software engineering or tech role often involves dozens of simultaneous applications, recruiter emails, technical take-home assignments, system design rounds, and follow-ups. Spreadsheets quickly become cluttered, outdated, and unhelpful.

**JobFlow** solves this by providing:
- A clean, modern SaaS-style user experience.
- Automated pipeline tracking from **Applied → Shortlisted → Interview → Offer (or Rejected)**.
- Detailed round tracking (Online Assessment, Technical Rounds, Managerial, HR, Final).
- Proactive follow-up reminder scheduling.
- Deep conversion metrics (Interview Rate %, Offer Rate %, Rejection Rate %, monthly timelines).
- Full REST API with standard HTTP response codes.

---

## 🛠️ Technology Stack

| Domain | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.14+, Flask 3.1 | Core application framework & routing |
| **ORM** | SQLAlchemy & Flask-SQLAlchemy | Object-Relational Mapping & parameterized database queries |
| **Database** | MySQL (via PyMySQL) / SQLite (tests) | Persistent relational data store |
| **Authentication** | Flask-Login & Werkzeug Security | Session management, password hashing, and protected routes |
| **Migrations** | Flask-Migrate & Alembic | Schema versioning and database migrations |
| **Forms & Security** | Flask-WTF & WTForms | Input validation & CSRF token protection |
| **Frontend** | HTML5, CSS3, JavaScript (ES6) | Responsive client interface |
| **UI Framework** | Bootstrap 5.3 & Bootstrap Icons | Modern responsive components and grids |
| **Data Visualization** | Chart.js 4.4 | Interactive donut, bar, line, and radar pipeline analytics |
| **Testing** | Pytest 9.1 | Automated unit and integration testing suite |
| **Environment** | python-dotenv | Secure `.env` configuration management |

---

## 🏛️ Architecture

JobFlow is built using the **Application Factory Pattern** and modular **Flask Blueprints**, cleanly separating presentation, business logic, data models, and services:

```text
jobflow/
│
├── app/
│   ├── __init__.py              # Application factory (create_app), error handlers, context processors
│   ├── extensions.py            # Extensions (db, migrate, login_manager, csrf)
│   ├── forms.py                 # Flask-WTF form definitions and field validation rules
│   │
│   ├── models/                  # SQLAlchemy Relational Models
│   │   ├── __init__.py          # Model exports
│   │   ├── user.py              # User model (hashed passwords, authentication)
│   │   ├── application.py       # Application model (status, priority, work modes)
│   │   ├── interview.py         # Interview rounds and status
│   │   ├── followup.py          # Scheduled communication touchpoints
│   │   └── note.py              # Reflection & preparation notes
│   │
│   ├── routes/                  # Presentation / Controllers (Blueprints)
│   │   ├── auth.py              # Landing, registration, login, logout
│   │   ├── dashboard.py         # Live KPIs, recent apps, upcoming interviews
│   │   ├── applications.py      # CRUD, filtering, search, sorting, status toggle
│   │   ├── interviews.py        # Interview calendar & round management
│   │   ├── followups.py         # Follow-up reminders and completion
│   │   ├── analytics.py         # Conversion rates & timeline graphs
│   │   ├── profile.py           # Account settings and password changes
│   │   └── api.py               # RESTful JSON API endpoints
│   │
│   ├── services/                # Business Logic Layer
│   │   ├── analytics_service.py # Database KPI calculations & chart series
│   │   └── application_service.py # Dynamic query filtering, search, and sorting
│   │
│   ├── templates/               # Jinja2 Templates
│   │   ├── base.html            # Main dashboard layout with sidebar & topbar
│   │   ├── landing.html         # Public SaaS landing page
│   │   ├── auth/                # Login & Registration views
│   │   ├── dashboard/           # Dashboard overview
│   │   ├── applications/        # List, Form, and Detail views
│   │   ├── interviews/          # Dedicated rounds view & scheduling form
│   │   ├── followups/           # Follow-up reminders & scheduling form
│   │   ├── analytics/           # Chart.js conversion charts & insight cards
│   │   ├── profile/             # Profile & security settings
│   │   └── errors/              # Custom 400, 401, 403, 404, 500 error pages
│   │
│   └── static/                  # Client-Side Assets
│       ├── css/style.css        # Custom modern SaaS styling
│       ├── js/                  # main.js, dashboard.js, analytics.js
│       └── images/logo.svg      # JobFlow vector branding
│
├── migrations/                  # Alembic migration scripts
├── tests/                       # Pytest test suite (100% pass)
│   ├── conftest.py              # Isolated test fixtures & in-memory SQLite config
│   ├── test_auth.py             # Registration, login, logout, password hashing
│   ├── test_applications.py     # Application CRUD, search, filter, sort
│   ├── test_interviews.py       # Interview round lifecycle
│   ├── test_followups.py        # Follow-up scheduling and completion
│   ├── test_authorization.py    # Strict multi-tenant user isolation checks
│   └── test_api.py              # REST API endpoint status codes & authorization
│
├── .env.example                 # Environment configuration template
├── .gitignore                   # Version control ignore rules
├── config.py                    # Multi-environment configuration classes
├── requirements.txt             # Pinned project dependencies
├── run.py                       # Application execution entrypoint
├── setup_db.py                  # MySQL database initialization script
├── seed.py                      # Demo data generator
└── PROJECT_GUIDE.md             # In-depth architectural & interview guide
```

---

## 🗄️ Database Design & Entity Relationships

The relational database architecture guarantees strict user data isolation and cascade management:

```mermaid
erDiagram
    User ||--o{ Application : owns
    User ||--o{ Note : writes
    Application ||--o{ Interview : contains
    Application ||--o{ FollowUp : contains
    Application ||--o{ Note : contains

    User {
        int id PK
        string name
        string email UK
        string password_hash
        datetime created_at
        datetime updated_at
    }

    Application {
        int id PK
        int user_id FK
        string company_name
        string job_title
        string location
        string employment_type
        string work_mode
        string salary
        string job_url
        date application_date
        string status
        string priority
        string recruiter_name
        string recruiter_email
        text job_description
        text notes
        datetime created_at
        datetime updated_at
    }

    Interview {
        int id PK
        int application_id FK
        date interview_date
        string start_time
        string round_name
        string interview_type
        string meeting_link
        string interviewer
        string status
        text notes
        datetime created_at
        datetime updated_at
    }

    FollowUp {
        int id PK
        int application_id FK
        date followup_date
        string followup_type
        string status
        text notes
        datetime created_at
        datetime updated_at
    }

    Note {
        int id PK
        int application_id FK
        int user_id FK
        text content
        datetime created_at
        datetime updated_at
    }
```

- **Cascade Deletion**: When an application is deleted, all related interviews, follow-ups, and notes are automatically removed via `cascade="all, delete-orphan"`.
- **Indexed Columns**: Indexes are defined on frequently filtered fields (`user_id`, `company_name`, `job_title`, `status`, `priority`, `application_date`, `interview_date`).

---

## ⚙️ Installation & Setup

### 1. Clone & Enter Project Directory
```bash
cd "d:\Python Projects\jobflow"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to configure your MySQL credentials:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=generate_a_secure_random_hex_key

# MySQL Configuration:
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=jobflow_db

# Optional direct URI (MySQL):
# DATABASE_URL=mysql+pymysql://root:your_mysql_password@localhost:3306/jobflow_db?charset=utf8mb4

# For standalone offline testing without MySQL:
# DATABASE_URL=sqlite:///jobflow_dev.db
```

### 4. Create Database & Apply Migrations
Initialize the MySQL database and apply the Alembic schema migrations:
```bash
python setup_db.py
```
Or manually create your database in MySQL and run:
```bash
flask db upgrade
```
> **Note on Migrations**: JobFlow relies on versioned Alembic migrations (`flask db upgrade`) to manage schemas. Normal application startup does **not** call `db.create_all()`.

---

## 🗃️ Database Migrations (Flask-Migrate)

JobFlow includes built-in migration support using Alembic:

- **Apply migrations to the database** (creates/updates all tables):
  ```bash
  flask db upgrade
  ```
- **Generate a new migration script** after modifying models:
  ```bash
  flask db migrate -m "Description of changes"
  ```
- **Roll back to a previous migration**:
  ```bash
  flask db downgrade
  ```
- **Check current database revision**:
  ```bash
  flask db current
  ```

---

## 🏃 Running the Application

Start the Flask development server:
```bash
python run.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

### Seeding Development / Demo Data
To immediately populate the database with realistic applications (Google, Stripe, Datadog, Netflix, AWS), interviews, follow-ups, and notes:
```bash
python seed.py
```
**Demo Account Credentials:**
- **Email**: `demo@jobflow.dev`
- **Password**: `Demo1234!`

---

## 🧪 Running Automated Tests

JobFlow includes an automated Pytest test suite covering registration, login, logout, application CRUD, search, multi-field filtering, interview scheduling, follow-ups, strict user authorization isolation, and REST APIs.

Tests execute using SQLite in-memory with `StaticPool` and **never touch or alter your development or production MySQL database**.

Run tests with:
```bash
pytest -v
```

**Test Execution Results:**
```text
tests/test_api.py .......                                                [ 23%]
tests/test_applications.py ......                                        [ 43%]
tests/test_auth.py ......                                                [ 63%]
tests/test_authorization.py ...                                          [ 73%]
tests/test_followups.py ...                                              [ 83%]
tests/test_interviews.py ..                                              [ 90%]
tests/test_views.py ...                                                  [100%]

============================= 30 passed in 4.02s ==============================
```

---

## 📡 REST API Documentation

All API endpoints reside under `/api/` and return clean JSON with proper HTTP status codes.

### API Authentication & CSRF Architecture
JobFlow implements a dual-mode API authentication and CSRF protection architecture:

1. **Programmatic API Clients (HTTP Basic Authentication)**:
   - Header: `Authorization: Basic <base64(email:password)>`
   - Explicit credentials are passed directly in request headers (no ambient browser cookies).
   - **No CSRF token required**, enabling scripts, mobile clients, and third-party integrations to interact seamlessly with the API.

2. **Browser-Based Clients (Session Authentication)**:
   - When a browser user calls the API using their active session cookie:
     - **Safe read-only requests (`GET`)** succeed without CSRF tokens.
     - **State-changing requests (`POST`, `PUT`, `PATCH`, `DELETE`)** **MUST** provide a valid CSRF token in the `X-CSRFToken` or `X-CSRF-Token` header.
   - This prevents Cross-Site Request Forgery (CSRF) from malicious third-party websites while preserving full REST API functionality.

3. **Standard Web Forms**:
   - Web views (`/applications/new`, `/interviews/new`, etc.) continue to be protected by standard Flask-WTF CSRF form tokens (`form.hidden_tag()`).

### Applications Endpoints

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/api/applications` | List authenticated user's applications (supports `?status=` and `?priority=`) | `200`, `401` |
| `POST` | `/api/applications` | Create new application (requires CSRF if session-authenticated) | `201`, `400`, `401` |
| `GET` | `/api/applications/<id>` | Retrieve single application details | `200`, `401`, `403`, `404` |
| `PUT` | `/api/applications/<id>` | Update an application (requires CSRF if session-authenticated) | `200`, `400`, `401`, `403`, `404` |
| `DELETE` | `/api/applications/<id>` | Delete application & cascading records (requires CSRF if session-authenticated) | `200`, `401`, `403`, `404` |

#### Example: POST /api/applications
**Request Payload:**
```json
{
  "company_name": "Stripe",
  "job_title": "Backend Software Engineer",
  "location": "San Francisco, CA / Remote",
  "employment_type": "Full Time",
  "work_mode": "Remote",
  "salary": "$170,000",
  "application_date": "2026-10-05",
  "status": "Applied",
  "priority": "High"
}
```

**Response (HTTP 201 Created):**
```json
{
  "success": true,
  "message": "Application created successfully.",
  "data": {
    "id": 1,
    "user_id": 1,
    "company_name": "Stripe",
    "job_title": "Backend Software Engineer",
    "status": "Applied",
    "priority": "High",
    "created_at": "2026-10-05T09:40:00Z"
  }
}
```

### Interviews Endpoints

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/api/interviews` | List all user's scheduled & completed rounds | `200`, `401` |
| `POST` | `/api/interviews` | Schedule new interview round for an application | `201`, `400`, `401`, `403`, `404` |
| `GET` | `/api/interviews/<id>` | Retrieve single interview round details | `200`, `401`, `403`, `404` |
| `PUT` | `/api/interviews/<id>` | Update interview round details or status | `200`, `400`, `401`, `403`, `404` |
| `DELETE` | `/api/interviews/<id>` | Delete an interview round | `200`, `401`, `403`, `404` |

---

## 🔒 Security & Data Isolation Guarantees

1. **Password Hashing**: Stored using PBKDF2 with SHA-256 via Werkzeug Security. Plaintext passwords are never logged or stored.
2. **Multi-Tenant User Isolation**: Every database query verifies `Application.user_id == current_user.id`. Changing an ID in the URL returns `404 Not Found` rather than leaking other users' data.
3. **CSRF Protection**: All web forms require a cryptographically signed CSRF token from `Flask-WTF`.
4. **SQL Injection Resistance**: All database operations use SQLAlchemy ORM parameter binding.
5. **Open Redirect Mitigation**: Login redirects validate `urlsplit(next_page).netloc == ''` to ensure users are only redirected to internal application routes.
6. **Custom Error Pages**: Friendly, informative error pages for `400`, `401`, `403`, `404`, and `500` without exposing raw stack traces.

---

## 🔮 Future Improvements

1. **Email / Calendar Integration**: Automated Google Calendar / Outlook sync for scheduled interview rounds.
2. **Resume Parser**: PDF resume upload with automated keyword extraction against job descriptions.
3. **Kanban Drag-and-Drop View**: Interactive drag-and-drop board for stage progression.
4. **Browser Extension**: 1-click web clipper to save jobs directly from LinkedIn, Indeed, and Greenhouse.
