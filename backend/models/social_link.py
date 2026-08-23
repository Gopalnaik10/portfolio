from datetime import datetime, timezone
from . import db

class SocialLink(db.Model):
    __tablename__ = 'social_links'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), default="link")
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'icon': self.icon,
            'enabled': self.enabled,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
