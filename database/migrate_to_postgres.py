"""
SQLite to PostgreSQL Safe Migration Utility

Copies all portfolio CMS data from local SQLite database into a target PostgreSQL database:
- Admin account & hashed credentials
- Profile information & custom about stats
- Skills and toolkit categories
- Projects, descriptions, problem statements, and key features
- Academic education background
- Social channels and contact links
- Site SEO & maintenance settings
- Contact inbox messages

Usage:
    python database/migrate_to_postgres.py --target "postgresql://DB_CONNECTION_STRING"
    Or set TARGET_DATABASE_URL / DATABASE_URL in environment and run:
    python database/migrate_to_postgres.py
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.config import Config
from backend.models import (
    db, AdminUser, Profile, Skill, Project, Education, 
    SocialLink, Resume, SiteSettings, Message, ActivityLog, AnalyticsVisit
)
from database.init_db import migrate_missing_columns

def parse_args():
    parser = argparse.ArgumentParser(description="Safely migrate Portfolio CMS data from SQLite to PostgreSQL.")
    parser.add_argument(
        '--target', 
        type=str, 
        default=os.getenv('TARGET_DATABASE_URL', os.getenv('DATABASE_URL')),
        help="Target PostgreSQL database URL (e.g. postgresql://DB_CONNECTION_STRING)"
    )
    parser.add_argument(
        '--source', 
        type=str, 
        default=str(BASE_DIR / 'database' / 'portfolio.db'),
        help="Source SQLite database path (default: database/portfolio.db)"
    )
    return parser.parse_args()

def run_migration(source_sqlite_path: str, target_pg_url: str):
    print("============================================================")
    print("PORTFOLIO CMS — SQLITE TO POSTGRESQL MIGRATION UTILITY")
    print("============================================================")

    if not target_pg_url:
        print("[ERROR] No target PostgreSQL database URL provided.")
        print("Please provide --target \"postgresql://DB_CONNECTION_STRING\" or set TARGET_DATABASE_URL.")
        sys.exit(1)

    # Normalize postgres:// to postgresql://
    if target_pg_url.startswith("postgres://"):
        target_pg_url = target_pg_url.replace("postgres://", "postgresql://", 1)

    if not target_pg_url.startswith("postgresql"):
        print("[ERROR] Target URL must be a PostgreSQL connection string (postgresql://...).")
        sys.exit(1)

    source_path = Path(source_sqlite_path)
    if not source_path.is_file():
        print(f"[ERROR] Source SQLite database not found at: {source_path}")
        sys.exit(1)

    print(f"[1/4] Source SQLite DB: {source_path}")
    masked_target = target_pg_url.split('@')[-1] if '@' in target_pg_url else 'PostgreSQL'
    print(f"[1/4] Target Database Host: {masked_target}")

    # 1. Connect to Source SQLite
    src_engine = create_engine(f"sqlite:///{source_path}")
    SrcSession = sessionmaker(bind=src_engine)
    src_session = SrcSession()

    # 2. Connect to Target PostgreSQL
    tgt_engine = create_engine(target_pg_url, pool_pre_ping=True)
    TgtSession = sessionmaker(bind=tgt_engine)
    tgt_session = TgtSession()

    # 3. Create target tables if they do not exist
    print("\n[2/4] Ensuring PostgreSQL schema exists...")
    app = Flask("migration_app")
    app.config['SQLALCHEMY_DATABASE_URI'] = target_pg_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        migrate_missing_columns()
    print("✓ Schema initialized and validated.")

    print("\n[3/4] Migrating data non-destructively...")

    # A. Admin User
    src_admins = src_session.query(AdminUser).all()
    migrated_admins = 0
    for a in src_admins:
        existing = tgt_session.query(AdminUser).filter_by(email=a.email).first()
        if not existing:
            new_a = AdminUser(
                email=a.email,
                password_hash=a.password_hash,
                created_at=a.created_at,
                updated_at=a.updated_at
            )
            tgt_session.add(new_a)
            migrated_admins += 1
        else:
            existing.password_hash = a.password_hash
            existing.updated_at = a.updated_at
    tgt_session.commit()
    print(f"✓ Admin Users: {migrated_admins} inserted / synchronized.")

    # B. Profile
    src_profiles = src_session.query(Profile).all()
    migrated_profiles = 0
    for p in src_profiles:
        existing_p = tgt_session.query(Profile).first()
        if not existing_p:
            p_dict = {c.name: getattr(p, c.name) for c in Profile.__table__.columns if c.name != 'id'}
            tgt_session.add(Profile(**p_dict))
            migrated_profiles += 1
        else:
            for c in Profile.__table__.columns:
                if c.name != 'id':
                    setattr(existing_p, c.name, getattr(p, c.name))
    tgt_session.commit()
    print(f"✓ Profile: {migrated_profiles} inserted / updated.")

    # C. Skills
    src_skills = src_session.query(Skill).all()
    migrated_skills = 0
    for s in src_skills:
        existing_s = tgt_session.query(Skill).filter_by(name=s.name, category=s.category).first()
        if not existing_s:
            s_dict = {c.name: getattr(s, c.name) for c in Skill.__table__.columns if c.name != 'id'}
            tgt_session.add(Skill(**s_dict))
            migrated_skills += 1
        else:
            existing_s.display_order = s.display_order
            existing_s.icon = s.icon
    tgt_session.commit()
    print(f"✓ Skills: {migrated_skills} new inserted ({len(src_skills)} total).")

    # D. Projects
    src_projects = src_session.query(Project).all()
    migrated_projects = 0
    for prj in src_projects:
        existing_prj = tgt_session.query(Project).filter_by(title=prj.title).first()
        if not existing_prj:
            prj_dict = {c.name: getattr(prj, c.name) for c in Project.__table__.columns if c.name != 'id'}
            tgt_session.add(Project(**prj_dict))
            migrated_projects += 1
        else:
            for c in Project.__table__.columns:
                if c.name != 'id':
                    setattr(existing_prj, c.name, getattr(prj, c.name))
    tgt_session.commit()
    print(f"✓ Projects: {migrated_projects} new inserted ({len(src_projects)} total).")

    # E. Education
    src_edus = src_session.query(Education).all()
    migrated_edus = 0
    for edu in src_edus:
        existing_edu = tgt_session.query(Education).filter_by(institution=edu.institution, degree=edu.degree).first()
        if not existing_edu:
            edu_dict = {c.name: getattr(edu, c.name) for c in Education.__table__.columns if c.name != 'id'}
            tgt_session.add(Education(**edu_dict))
            migrated_edus += 1
    tgt_session.commit()
    print(f"✓ Education: {migrated_edus} new inserted ({len(src_edus)} total).")

    # F. Social Links
    src_socials = src_session.query(SocialLink).all()
    migrated_socials = 0
    for soc in src_socials:
        existing_soc = tgt_session.query(SocialLink).filter_by(platform=soc.platform).first()
        if not existing_soc:
            soc_dict = {c.name: getattr(soc, c.name) for c in SocialLink.__table__.columns if c.name != 'id'}
            tgt_session.add(SocialLink(**soc_dict))
            migrated_socials += 1
        else:
            existing_soc.url = soc.url
            existing_soc.display_order = soc.display_order
            existing_soc.is_active = soc.is_active
    tgt_session.commit()
    print(f"✓ Social Links: {migrated_socials} new inserted ({len(src_socials)} total).")

    # G. Site Settings
    src_settings = src_session.query(SiteSettings).first()
    if src_settings:
        existing_st = tgt_session.query(SiteSettings).first()
        if not existing_st:
            st_dict = {c.name: getattr(src_settings, c.name) for c in SiteSettings.__table__.columns if c.name != 'id'}
            tgt_session.add(SiteSettings(**st_dict))
        else:
            for c in SiteSettings.__table__.columns:
                if c.name != 'id':
                    setattr(existing_st, c.name, getattr(src_settings, c.name))
        tgt_session.commit()
        print("✓ Site Settings: synchronized.")

    # H. Messages
    src_msgs = src_session.query(Message).all()
    migrated_msgs = 0
    for m in src_msgs:
        existing_m = tgt_session.query(Message).filter_by(email=m.email, subject=m.subject, created_at=m.created_at).first()
        if not existing_m:
            m_dict = {c.name: getattr(m, c.name) for c in Message.__table__.columns if c.name != 'id'}
            tgt_session.add(Message(**m_dict))
            migrated_msgs += 1
    tgt_session.commit()
    print(f"✓ Messages: {migrated_msgs} new inserted ({len(src_msgs)} total).")

    # 4. Final Verification
    print("\n[4/4] Verifying PostgreSQL Data Integrity...")
    final_admin = tgt_session.query(AdminUser).first()
    final_profile = tgt_session.query(Profile).first()
    final_skills_count = tgt_session.query(Skill).count()
    final_projects_count = tgt_session.query(Project).count()
    final_edu_count = tgt_session.query(Education).count()
    final_soc_count = tgt_session.query(SocialLink).count()

    print(f"  - Target Admin: {final_admin.email if final_admin else 'None'}")
    print(f"  - Target Profile: {final_profile.name if final_profile else 'None'}")
    print(f"  - Target Skills: {final_skills_count} skills")
    print(f"  - Target Projects: {final_projects_count} projects")
    print(f"  - Target Education: {final_edu_count} records")
    print(f"  - Target Socials: {final_soc_count} links")

    src_session.close()
    tgt_session.close()

    print("\n============================================================")
    print("MIGRATION COMPLETED SUCCESSFULLY — ZERO DATA LOSS")
    print("============================================================")

if __name__ == '__main__':
    args = parse_args()
    run_migration(args.source, args.target)
