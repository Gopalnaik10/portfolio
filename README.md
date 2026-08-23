# Gopal Naik — Portfolio CMS

A full-stack personal portfolio website with a **private Admin CMS** for managing all content without touching source code.

```
ONE APPLICATION
│
├── Public Portfolio   /            (no login required)
└── Admin CMS          /admin       (authenticated access only)
```

---

## Architecture

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ / Flask 3.x |
| Database | SQLite (dev) / PostgreSQL (production) |
| ORM | SQLAlchemy 2.x |
| Auth | Flask sessions + Werkzeug password hashing |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Production | Gunicorn WSGI server |

---

## Required Environment Variables

Create a `.env` file in the project root. **Never commit this file to Git.**

```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generate-a-long-random-string-min-32-chars>

# Server
HOST=0.0.0.0
PORT=5000

# Database
# Development: leave as SQLite default (no DATABASE_URL needed)
# Production: set your PostgreSQL connection string
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Admin account (first-run only, change immediately after first login)
ADMIN_EMAIL=your.admin.email@example.com
ADMIN_DEFAULT_PASSWORD=<strong-password-min-12-chars>
```

> **Never put real credentials in `.env.example` or this README.**

### Generate a secure SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/portfolio.git
cd portfolio
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

Copy the example and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your real values (see **Required Environment Variables** above).

---

## Database Setup

### Development (SQLite — automatic)

The database is created automatically on first run. No configuration required.

```bash
python database/init_db.py
```

### Production (PostgreSQL)

1. Create a PostgreSQL database and user:

```sql
CREATE DATABASE portfolio_db;
CREATE USER portfolio_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO portfolio_user;
```

2. Set `DATABASE_URL` in your environment:

```env
DATABASE_URL=postgresql://portfolio_user:yourpassword@localhost:5432/portfolio_db
```

3. Initialize the schema:

```bash
python database/init_db.py
```

This creates all tables and seeds the initial portfolio data if the database is empty.

---

## Running Locally

```bash
python backend/app.py
```

The server starts at `http://127.0.0.1:5000`

- **Public portfolio:** `http://127.0.0.1:5000/`
- **Admin login:** `http://127.0.0.1:5000/admin`

---

## Running in Production

### With Gunicorn (recommended)

```bash
gunicorn backend.app:app --bind 0.0.0.0:5000 --workers 2
```

### With environment variables inline

```bash
FLASK_ENV=production FLASK_DEBUG=False gunicorn backend.app:app --bind 0.0.0.0:$PORT
```

### Procfile (Render / Railway / Heroku)

A `Procfile` is included:

```
web: gunicorn "backend.app:create_app()"
```

---

## Deploying to Render

1. **Create a PostgreSQL Database on Render:**
   - On the Render Dashboard, click **New +** → **PostgreSQL**.
   - Copy the **Internal Database URL** (or External URL).

2. **Create a Web Service on Render:**
   - Click **New +** → **Web Service** and connect your GitHub repository.
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn "backend.app:create_app()"`

3. **Set Environment Variables in Render Dashboard:**
   - `DATABASE_URL`: Your Render PostgreSQL database URL.
   - `SECRET_KEY`: A secure 64-character random string (`python -c "import secrets; print(secrets.token_hex(32))"`).
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`
   - `ADMIN_EMAIL`: Your initial admin login email.
   - `ADMIN_DEFAULT_PASSWORD`: Strong temporary password (change upon login).

4. **Persistent Disk (Optional for Uploads):**
   - For permanent file upload storage on Render across instance restarts, attach a **Persistent Disk** mounted at `/opt/render/project/src/uploads` with size `1 GB`.

---

## Admin Account

On first run, an admin account is automatically created using `ADMIN_EMAIL` and `ADMIN_DEFAULT_PASSWORD` from your `.env`.

**Change your password immediately after first login:**

1. Log in at `/admin`
2. Go to **Settings** tab
3. Use the **Change Password** form

> Passwords are stored as Werkzeug `pbkdf2:sha256` hashes. Plain text passwords are never stored.

---

## URL Structure

| URL | Description | Auth Required |
|---|---|---|
| `/` | Public portfolio | No |
| `/admin` | Redirects to login or dashboard | — |
| `/admin/login` | Admin login page | No |
| `/admin/dashboard` | Admin CMS dashboard | Yes |
| `/api/public/portfolio` | Public portfolio data API | No |
| `/api/public/contact` | Contact form submission | No |
| `/api/public/resume/download` | Resume download | No |
| `/api/auth/login` | Admin authentication | No |
| `/api/auth/logout` | Session logout | Yes |
| `/api/admin/*` | All admin CRUD APIs | Yes |

---

## Admin CMS Sections

| Tab | Manages |
|---|---|
| Dashboard | Stats, analytics, recent activity |
| Profile & Hero | Name, title, tagline, profile image, CTAs |
| Skills | Add / edit / delete / reorder skills |
| Projects | Add / edit / delete / upload images, GitHub/live URLs |
| Education | Degree, institution, years, coursework |
| Resume PDF | Upload downloadable CV |
| Social Links | GitHub, LinkedIn, Email, other links |
| Messages | Inbox of contact form submissions |
| Settings & SEO | Page title, meta description, maintenance mode, password change |

---

## Security Summary

- Passwords: hashed with Werkzeug `pbkdf2:sha256` — never stored in plain text
- Sessions: server-side Flask sessions with `SESSION_COOKIE_HTTPONLY = True`
- Admin routes: guarded by `@admin_required` decorator (server-side, not just JS)
- File uploads: restricted to `jpg`, `jpeg`, `png`, `webp` only (SVG excluded — XSS risk)
- File size limit: 20 MB max
- `.env` file: excluded from Git via `.gitignore`
- Debug mode: controlled by `FLASK_DEBUG` env var (must be `False` in production)
- Error pages: custom handlers for 400/403/404/500 — no stack traces exposed

---

## Deployment Checklist

Before deploying to production:

- [ ] `FLASK_DEBUG=False` in environment
- [ ] `FLASK_ENV=production` in environment
- [ ] `SECRET_KEY` set to a long random value (min 32 chars)
- [ ] `DATABASE_URL` set to production PostgreSQL connection string
- [ ] `ADMIN_EMAIL` and `ADMIN_DEFAULT_PASSWORD` set
- [ ] `.env` is NOT committed to Git
- [ ] `python database/init_db.py` run on the production server
- [ ] Admin password changed immediately after first login
- [ ] HTTPS configured on the production domain
- [ ] `gunicorn` is the WSGI server (not `flask run` or `python app.py`)

---

## File Structure

```
portfolio/
├── backend/
│   ├── app.py              # Flask application factory + error handlers
│   ├── config.py           # Configuration from environment variables
│   ├── models/             # SQLAlchemy ORM models
│   ├── routes/             # Blueprint route handlers
│   ├── services/           # Business logic layer
│   └── utils/              # Auth decorators, validators
├── frontend/
│   ├── index.html          # Public portfolio SPA
│   ├── css/style.css       # Public design system
│   └── js/script.js        # Public portfolio JavaScript
├── admin/
│   ├── login.html          # Admin login page
│   ├── dashboard.html      # Admin CMS dashboard
│   ├── css/admin.css       # Admin design system
│   └── js/admin.js         # Admin CMS JavaScript
├── database/
│   ├── init_db.py          # Schema creation and seeding
│   └── seed_data.py        # Initial portfolio content
├── uploads/                # User-uploaded files (gitignored)
│   ├── profile/
│   ├── projects/
│   └── resume/
├── .env                    # Local secrets (NEVER commit)
├── .env.example            # Template (safe to commit)
├── .gitignore              # Ignores .env, *.db, uploads/
├── Procfile                # Production WSGI entry point
└── requirements.txt        # Python dependencies
```
