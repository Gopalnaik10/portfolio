from datetime import datetime, timezone
from . import db

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False, default="Core Languages")
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), default="code")
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'name': self.name,
            'icon': self.icon,
            'enabled': self.enabled,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
