import sys
from pathlib import Path
from sqlalchemy import inspect, text

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import Config
from backend.models import (
    db, AdminUser, Profile, Skill, Project, Education, 
    SocialLink, SiteSettings, ActivityLog
)
from database.seed_data import (
    INITIAL_PROFILE, INITIAL_SKILLS, INITIAL_PROJECTS, 
    INITIAL_EDUCATION, INITIAL_SOCIALS
)
from flask import Flask

def migrate_missing_columns():
    """Safely adds missing columns to existing SQLite/PostgreSQL tables without losing data."""
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        # Migrate profiles table
        if 'profiles' in tables:
            existing_cols = [c['name'] for c in inspector.get_columns('profiles')]
            profile_additions = [
                ('about_heading', 'VARCHAR(200)', "'Turning Ideas Into Impactful Solutions'"),
                ('stat_1_val', 'VARCHAR(50)', "'4+'"),
                ('stat_1_label', 'VARCHAR(100)', "'Projects Built'"),
                ('stat_2_val', 'VARCHAR(50)', "'15+'"),
                ('stat_2_label', 'VARCHAR(100)', "'Technologies & Tools'"),
                ('stat_3_val', 'VARCHAR(50)', "'2026'"),
                ('stat_3_label', 'VARCHAR(100)', "'Expected Graduation'"),
                ('stat_4_val', 'VARCHAR(50)', "'Data Science'"),
                ('stat_4_label', 'VARCHAR(100)', "'Specialization'")
            ]
            for col_name, col_type, default_val in profile_additions:
                if col_name not in existing_cols:
                    db.session.execute(text(f"ALTER TABLE profiles ADD COLUMN {col_name} {col_type} DEFAULT {default_val}"))
                    db.session.commit()

        # Migrate projects table
        if 'projects' in tables:
            existing_cols = [c['name'] for c in inspector.get_columns('projects')]
            project_additions = [
                ('problem_statement', 'TEXT', "''"),
                ('key_features', 'TEXT', "''")
            ]
            for col_name, col_type, default_val in project_additions:
                if col_name not in existing_cols:
                    db.session.execute(text(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type} DEFAULT {default_val}"))
                    db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Non-fatal during first table creation
        pass

def init_database(app: Flask):
    """
    NON-DESTRUCTIVE DATABASE INITIALIZATION:
    - Creates tables if they don't exist.
    - Safely migrates missing columns without modifying existing row data.
    - Seeds default records ONLY IF the table is completely empty (count == 0).
    - NEVER resets, overwrites, or deletes existing saved records.
    """
    with app.app_context():
        db.create_all()
        migrate_missing_columns()

        # 1. Admin User (create only if no admin exists)
        if AdminUser.query.count() == 0:
            default_pw = Config.ADMIN_DEFAULT_PASSWORD
            if not default_pw:
                raise ValueError(
                    "CRITICAL CONFIGURATION ERROR: ADMIN_DEFAULT_PASSWORD environment variable is required "
                    "to create the initial admin account."
                )

            admin = AdminUser(email=Config.ADMIN_EMAIL)
            admin.set_password(default_pw)
            db.session.add(admin)
            db.session.add(ActivityLog(
                action_type="SYSTEM_INIT",
                description=f"Admin account created for {Config.ADMIN_EMAIL}"
            ))

        # 2. Profile (create only if table is empty)
        if Profile.query.count() == 0:
            profile = Profile(**INITIAL_PROFILE)
            db.session.add(profile)

        # 3. Skills (create only if table is empty)
        if Skill.query.count() == 0:
            for item in INITIAL_SKILLS:
                db.session.add(Skill(**item))

        # 4. Projects (create only if table is empty)
        if Project.query.count() == 0:
            for item in INITIAL_PROJECTS:
                db.session.add(Project(**item))

        # 5. Education (create only if table is empty)
        if Education.query.count() == 0:
            for item in INITIAL_EDUCATION:
                db.session.add(Education(**item))

        # 6. Social Links (create only if table is empty)
        if SocialLink.query.count() == 0:
            for item in INITIAL_SOCIALS:
                db.session.add(SocialLink(**item))

        # 7. Site Settings (create only if table is empty)
        if SiteSettings.query.count() == 0:
            settings = SiteSettings(
                site_title="Gopal Naik | Computer Science & Engineering | Data Science",
                meta_description="Personal portfolio of Gopal Naik, Computer Science & Engineering student specializing in Data Science and Full Stack Development."
            )
            db.session.add(settings)

        db.session.commit()
        print("[DB] Portfolio database verified & synchronized safely (non-destructive).")

if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    init_database(app)
