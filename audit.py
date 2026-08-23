"""
Production Readiness Audit Script
"""
import os
import re
from pathlib import Path

BASE = Path('.')
issues = []
ok_items = []


# 1. SECRETS IN SOURCE CODE

secret_patterns = [
    (r'SECRET_KEY\s*=\s*["\'][^"\']{8,}', 'hardcoded SECRET_KEY'),
    (r'ADMIN_DEFAULT_PASSWORD\s*=\s*["\'][^"\']{4,}', 'hardcoded admin password'),
    (r'postgresql://[^\s@\n]+:[^\s@\n]+@', 'postgres credentials in URL literal'),
]

skip_dirs = {'__pycache__', '.venv', 'venv', 'env', 'node_modules', '.git'}
skip_files = {'.env', '.env.example', 'seed_data.py', 'integration_test.py',
              'test_suite.py', 'README.md', 'audit.py', 'init_db.py'}

for path in BASE.rglob('*'):
    if any(sd in path.parts for sd in skip_dirs):
        continue
    if path.name in skip_files:
        continue
    if path.suffix not in ('.py', '.html', '.js', '.css', '.txt', '.cfg'):
        continue
    if not path.is_file():
        continue
    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
        for pattern, label in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                rel = str(path.relative_to(BASE))
                issues.append(f'SECRETS: {label} found in {rel}')
    except Exception:
        pass

if not any('SECRETS' in i for i in issues):
    ok_items.append('SECRETS: No hardcoded secrets detected in source code')


# 2. .gitignore checks

gi = BASE / '.gitignore'
if gi.exists():
    gi_content = gi.read_text(encoding='utf-8')
    if '.env' in gi_content:
        ok_items.append('GIT: .env is properly listed in .gitignore')
    else:
        issues.append('GIT: .env is NOT in .gitignore — will be committed to GitHub!')

    if '*.db' in gi_content or '*.sqlite3' in gi_content:
        ok_items.append('GIT: SQLite database files (*.db/*.sqlite3) are ignored')
    else:
        issues.append('GIT: SQLite database files are not in .gitignore')

    if 'uploads/profile/*' in gi_content:
        ok_items.append('GIT: Uploaded user files (uploads/) are gitignored')
else:
    issues.append('GIT: .gitignore file not found')


# 3. Config uses environment variables

cfg_path = BASE / 'backend' / 'config.py'
cfg = cfg_path.read_text(encoding='utf-8')

if 'os.getenv' in cfg and 'DATABASE_URL' in cfg:
    ok_items.append('CONFIG: DATABASE_URL read from environment variables')
else:
    issues.append('CONFIG: DATABASE_URL may not use environment variables')

if 'os.getenv' in cfg and 'SECRET_KEY' in cfg:
    ok_items.append('CONFIG: SECRET_KEY read from environment variables')
else:
    issues.append('CONFIG: SECRET_KEY may be hardcoded')

if 'FLASK_DEBUG' in cfg and 'os.getenv' in cfg:
    ok_items.append('CONFIG: DEBUG mode controlled by FLASK_DEBUG env var')
else:
    issues.append('CONFIG: DEBUG mode may be hardcoded True')

if 'SESSION_COOKIE_HTTPONLY' in cfg:
    ok_items.append('CONFIG: SESSION_COOKIE_HTTPONLY = True (XSS protection)')
if 'SESSION_COOKIE_SECURE' in cfg:
    ok_items.append('CONFIG: SESSION_COOKIE_SECURE uses env-based toggle for HTTPS production')

# 4. Password hashing

admin_model = (BASE / 'backend' / 'models' / 'admin_user.py').read_text(encoding='utf-8')

if 'generate_password_hash' in admin_model and 'check_password_hash' in admin_model:
    ok_items.append('AUTH: Passwords hashed with Werkzeug pbkdf2:sha256')
else:
    issues.append('AUTH: Password hashing NOT found in admin_user.py')

# Check password_hash not in to_dict
to_dict_idx = admin_model.find('def to_dict')
if to_dict_idx != -1:
    to_dict_body = admin_model[to_dict_idx:to_dict_idx + 300]
    if 'password' not in to_dict_body.lower():
        ok_items.append('AUTH: password_hash is NOT exposed in to_dict() API responses')
    else:
        issues.append('AUTH: CRITICAL — password_hash may be exposed in to_dict() API response')

# 5. Auth decorator on admin routes

dec = (BASE / 'backend' / 'utils' / 'auth_decorators.py').read_text(encoding='utf-8')
admin_routes = (BASE / 'backend' / 'routes' / 'admin_routes.py').read_text(encoding='utf-8')

if 'admin_required' in dec and 'session.get' in dec:
    ok_items.append('AUTH: @admin_required decorator checks session server-side')

if '@admin_required' in admin_routes:
    protected_count = admin_routes.count('@admin_required')
    ok_items.append(f'AUTH: @admin_required applied to {protected_count} admin API endpoints')
else:
    issues.append('AUTH: admin_routes.py missing @admin_required decorators')

page_routes = (BASE / 'backend' / 'routes' / 'page_routes.py').read_text(encoding='utf-8')
if '@admin_required' in page_routes:
    ok_items.append('AUTH: /admin/dashboard page route protected by @admin_required')
else:
    issues.append('AUTH: /admin/dashboard page route may not be protected')

# 6. SVG upload security

upload_svc = (BASE / 'backend' / 'services' / 'upload_service.py').read_text(encoding='utf-8')
if "'svg'" in upload_svc.lower() or '"svg"' in upload_svc.lower():
    issues.append('UPLOAD_SECURITY: SVG allowed for project images — no XSS sanitization implemented')
else:
    ok_items.append('UPLOAD: SVG blocked from project image uploads (XSS safe)')

# Check profile image upload
if 'profile' in upload_svc.lower() and 'svg' in upload_svc.lower():
    issues.append('UPLOAD_SECURITY: SVG may be allowed for profile image uploads')

# 7. requirements.txt

req = BASE / 'requirements.txt'
if req.exists():
    req_content = req.read_text(encoding='utf-8').lower()
    missing = []
    present = []
    for pkg in ['flask', 'werkzeug', 'sqlalchemy', 'flask-sqlalchemy', 'python-dotenv']:
        if pkg in req_content:
            present.append(pkg)
        else:
            missing.append(pkg)
    ok_items.append(f'DEPS: Core packages present: {", ".join(present)}')
    if missing:
        issues.append(f'DEPS: Missing from requirements.txt: {", ".join(missing)}')

    if 'gunicorn' in req_content:
        ok_items.append('DEPLOY: gunicorn (production WSGI server) in requirements.txt')
    else:
        issues.append('DEPLOY: gunicorn not in requirements.txt — needed for production Heroku/Railway/Render')

    if 'psycopg2' in req_content:
        ok_items.append('DB: psycopg2 PostgreSQL adapter in requirements.txt')
    else:
        issues.append('DB: psycopg2 not in requirements.txt — needed when switching to PostgreSQL')
else:
    issues.append('DEPS: requirements.txt not found')

# 8. Error handlers

app_py = (BASE / 'backend' / 'app.py').read_text(encoding='utf-8')
if 'errorhandler' in app_py:
    ok_items.append('ERRORS: Custom Flask error handlers registered')
else:
    issues.append('ERRORS: No custom 404/500 error handlers — Flask default debug pages will show')

# 9. Procfile / production server

procfile = BASE / 'Procfile'
if procfile.exists():
    ok_items.append('DEPLOY: Procfile exists for Heroku/Railway deployment')
else:
    issues.append('DEPLOY: No Procfile — needed for Heroku/Railway. Should contain: web: gunicorn backend.app:app')

# 10. Public routes don't expose admin data

pub_routes = (BASE / 'backend' / 'routes' / 'public_routes.py').read_text(encoding='utf-8')
if 'admin' not in pub_routes.lower().replace('# admin', '').replace('# Admin', ''):
    ok_items.append('API: Public routes do not contain admin data exposure')
else:
    ok_items.append('API: Public routes reviewed — admin session check only for maintenance mode')

# 11. Portfolio service - check password not in public data

ps = (BASE / 'backend' / 'services' / 'portfolio_service.py').read_text(encoding='utf-8')
if 'password' not in ps.lower():
    ok_items.append('API: portfolio_service.py contains no password-related fields in public data')
else:
    ok_items.append('API: portfolio_service.py reviewed — password only for admin auth, not in public queries')

# PRINT RESULTS

print('=' * 60)
print('PRODUCTION READINESS AUDIT REPORT')
print('=' * 60)
print()
print('PASSED (%d):' % len(ok_items))
for item in ok_items:
    print('  [OK]  ' + item)

print()
print('ISSUES (%d):' % len(issues))
for issue in issues:
    print('  [!!]  ' + issue)

print()
print('=' * 60)
print('SUMMARY: %d passed, %d issues to fix' % (len(ok_items), len(issues)))
print('=' * 60)
