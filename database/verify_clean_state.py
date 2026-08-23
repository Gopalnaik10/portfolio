import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.models import db, AdminUser, Message, ActivityLog, AnalyticsVisit, Project, Skill, Education, SocialLink, Profile

app = create_app()
with app.app_context():
    print("--- CURRENT DATABASE STATE ---")
    admin = AdminUser.query.first()
    print(f"Admin: {admin.email if admin else 'None'}")
    profile = Profile.query.first()
    print(f"Profile: {profile.name if profile else 'None'}")
    print(f"Skills: {Skill.query.count()} skills")
    print(f"Projects: {Project.query.count()} projects:")
    for p in Project.query.all():
        print(f"  [{p.id}] {p.title} (views: {p.view_count}) -> {p.short_description}")
    print(f"Education: {Education.query.count()} entries")
    print(f"Socials: {SocialLink.query.count()} links")
    print(f"Messages: {Message.query.count()} messages")
    print(f"Activity Logs: {ActivityLog.query.count()} logs")
    print(f"Analytics Visits: {AnalyticsVisit.query.count()} visits")
