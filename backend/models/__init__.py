"""
SQLAlchemy database instance and model exports.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .admin_user import AdminUser
from .profile import Profile
from .skill import Skill
from .project import Project
from .education import Education
from .social_link import SocialLink
from .resume import Resume
from .message import Message
from .site_settings import SiteSettings
from .activity import ActivityLog
from .analytics import AnalyticsVisit

__all__ = [
    'db',
    'AdminUser',
    'Profile',
    'Skill',
    'Project',
    'Education',
    'SocialLink',
    'Resume',
    'Message',
    'SiteSettings',
    'ActivityLog',
    'AnalyticsVisit'
]
