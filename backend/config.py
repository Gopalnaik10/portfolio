import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Resolve project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / '.env')

class Config:
    BASE_DIR = BASE_DIR

    # Environment Detection
    is_render = os.getenv('RENDER') == 'true' or os.getenv('RENDER_EXTERNAL_HOSTNAME') is not None
    is_prod = os.getenv('FLASK_ENV') == 'production' or is_render

    # Secret Key Configuration
    _raw_secret = os.getenv('SECRET_KEY')
    if is_prod and not _raw_secret:
        raise ValueError(
            "CRITICAL CONFIGURATION ERROR: SECRET_KEY environment variable is required in production. "
            "Please set a strong, random SECRET_KEY in your Render dashboard environment variables."
        )
    SECRET_KEY = _raw_secret or 'dev-insecure-secret-key-for-local-development-only'
    
    # Database Configuration
    raw_db_url = os.getenv('DATABASE_URL')
    if is_prod:
        if not raw_db_url:
            raise ValueError(
                "CRITICAL CONFIGURATION ERROR: DATABASE_URL environment variable is required in production. "
                "Please provision a PostgreSQL database (e.g. Render PostgreSQL, Supabase, Neon) and set DATABASE_URL."
            )
        if raw_db_url.startswith("sqlite"):
            raise ValueError(
                "CRITICAL CONFIGURATION ERROR: SQLite cannot be used in production because cloud containers use an ephemeral filesystem. "
                "Please configure DATABASE_URL to point to a persistent PostgreSQL database."
            )

    if not raw_db_url:
        raw_db_url = f"sqlite:///{BASE_DIR / 'database' / 'portfolio.db'}"

    # Normalize postgres:// to postgresql:// for SQLAlchemy 2.0+
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    elif raw_db_url.startswith("sqlite:///"):
        # Ensure database directory exists for SQLite in local development
        db_path = raw_db_url.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            abs_db_path = BASE_DIR / db_path
            abs_db_path.parent.mkdir(parents=True, exist_ok=True)
            raw_db_url = f"sqlite:///{abs_db_path}"

    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20
    } if not raw_db_url.startswith("sqlite") else {}

    # Uploads & Persistent Storage Configuration
    raw_upload_dir = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    try:
        target_upload_path = Path(raw_upload_dir) if os.path.isabs(raw_upload_dir) else (BASE_DIR / raw_upload_dir)
        target_upload_path.mkdir(parents=True, exist_ok=True)
        (target_upload_path / 'profile').mkdir(parents=True, exist_ok=True)
        (target_upload_path / 'projects').mkdir(parents=True, exist_ok=True)
        (target_upload_path / 'resume').mkdir(parents=True, exist_ok=True)
        UPLOAD_FOLDER = target_upload_path
    except (PermissionError, OSError):
        fallback_upload_path = BASE_DIR / 'uploads'
        fallback_upload_path.mkdir(parents=True, exist_ok=True)
        (fallback_upload_path / 'profile').mkdir(parents=True, exist_ok=True)
        (fallback_upload_path / 'projects').mkdir(parents=True, exist_ok=True)
        (fallback_upload_path / 'resume').mkdir(parents=True, exist_ok=True)
        UPLOAD_FOLDER = fallback_upload_path

    # Cloudinary Image Storage Configuration (Production & Cloud Hosting)
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '').strip()
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '').strip()
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '').strip()
    is_cloudinary_configured = bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)

    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB max file size
    # Image uploads: JPG, JPEG, PNG, WebP only.
    # SVG excluded — no server-side sanitizer, XSS risk via embedded scripts.
    # GIF excluded — animated images not needed in portfolio context.
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    ALLOWED_DOC_EXTENSIONS = {'pdf'}

    # Session & Security Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = is_prod or os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Server Defaults
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0' if is_render else '127.0.0.1')
    DEBUG = os.getenv('FLASK_DEBUG', 'False' if is_prod else 'True').lower() in ('true', '1', 't')

    # Seed Admin Defaults
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@portfolio.local')
    ADMIN_DEFAULT_PASSWORD = os.getenv('ADMIN_DEFAULT_PASSWORD')

    # SMTP & Email Notification Settings (server-side only)
    MAIL_SERVER = os.getenv('MAIL_SERVER', '').strip()
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() in ('true', '1', 't') or MAIL_PORT == 465
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '').strip()
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '').strip()
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME', 'noreply@portfolio.local')).strip()
    MAIL_RECIPIENT = os.getenv('MAIL_RECIPIENT', os.getenv('ADMIN_NOTIFICATION_EMAIL', os.getenv('ADMIN_EMAIL', 'admin@portfolio.local'))).strip()
    ADMIN_NOTIFICATION_EMAIL = MAIL_RECIPIENT
