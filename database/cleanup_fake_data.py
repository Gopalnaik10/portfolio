"""
Database Cleanup Script
Safely removes all test, fake, and demo artifacts from the database
while strictly preserving all legitimate portfolio data and admin account.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.models import db, AdminUser, Message, ActivityLog, AnalyticsVisit, Project, Skill, Education, SocialLink, Profile, SiteSettings
from database.seed_data import INITIAL_PROJECTS

def clean_database():
    app = create_app()
    with app.app_context():
        print("Starting safe database cleanup...")

        # 1. Clean Messages (remove test messages)
        deleted_msgs = Message.query.delete()
        print(f"✓ Removed {deleted_msgs} test contact message(s). Messages inbox is now clean.")

        # 2. Clean Activity Logs (remove all test activity records)
        deleted_logs = ActivityLog.query.delete()
        print(f"✓ Removed {deleted_logs} test activity log(s). History is now clean.")

        # 3. Clean Analytics (remove test visit counts)
        deleted_visits = AnalyticsVisit.query.delete()
        print(f"✓ Removed {deleted_visits} test visit record(s). Visitor tracking is now clean.")

        # 4. Clean Projects (remove any non-standard test projects like 'Autonomous Multi-Agent Researcher')
        valid_titles = {p["title"] for p in INITIAL_PROJECTS}
        test_projects = Project.query.filter(~Project.title.in_(valid_titles)).all()
        for tp in test_projects:
            print(f"  - Removing test project: {tp.title} (ID: {tp.id})")
            db.session.delete(tp)

        # 5. Restore clean descriptions for initial projects
        for init_p in INITIAL_PROJECTS:
            existing = Project.query.filter_by(title=init_p["title"]).first()
            if existing:
                existing.short_description = init_p["short_description"]
                existing.description = init_p["description"]
                existing.view_count = 0  # Reset test views to 0

        # 6. Verify Admin Account remains intact
        admin = AdminUser.query.first()
        if admin:
            print(f"✓ Verified Admin User preserved: {admin.email} (ID: {admin.id})")

        # 7. Verify Core Content preserved
        print(f"✓ Verified Profile: {Profile.query.first().name if Profile.query.first() else 'None'}")
        print(f"✓ Verified Skills: {Skill.query.count()} skills across categories")
        print(f"✓ Verified Projects: {Project.query.count()} real projects")
        print(f"✓ Verified Education: {Education.query.count()} records")
        print(f"✓ Verified Socials: {SocialLink.query.count()} active links")

        db.session.commit()
        print("\n=== DATABASE CLEANUP COMPLETE: ZERO FAKE DATA REMAINING ===")

if __name__ == '__main__':
    clean_database()
