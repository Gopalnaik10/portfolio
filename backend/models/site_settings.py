from datetime import datetime, timezone
from . import db

class SiteSettings(db.Model):
    __tablename__ = 'site_settings'

    id = db.Column(db.Integer, primary_key=True)
    site_title = db.Column(db.String(200), default="[Your Name] | Computer Science & Data Science Portfolio")
    meta_description = db.Column(db.String(300), default="Personal portfolio of [Your Name], Computer Science & Engineering student specializing in Data Science and Machine Learning.")
    keywords = db.Column(db.String(300), default="Data Science, Machine Learning, Computer Science, Portfolio, Python, Software Engineering")
    og_image = db.Column(db.String(255), default="/assets/avatar-placeholder.svg")
    maintenance_mode = db.Column(db.Boolean, default=False, nullable=False)
    maintenance_message = db.Column(db.String(500), default="Our portfolio is undergoing scheduled maintenance. Please check back shortly or connect via email.")
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'site_title': self.site_title,
            'meta_description': self.meta_description,
            'keywords': self.keywords,
            'og_image': self.og_image,
            'maintenance_mode': self.maintenance_mode,
            'maintenance_message': self.maintenance_message,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
