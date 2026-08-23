from datetime import datetime, timezone
from . import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False) # e.g. "PROJECT_UPDATED", "RESUME_UPLOADED", "MESSAGE_RECEIVED"
    description = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'action_type': self.action_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'formatted_time': self.created_at.strftime('%b %d, %Y - %I:%M %p') if self.created_at else ''
        }
