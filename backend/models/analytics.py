from datetime import datetime, timezone
from . import db

class AnalyticsVisit(db.Model):
    __tablename__ = 'analytics_visits'

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100), default="/", nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    ip_hash = db.Column(db.String(64), nullable=True) # Anonymized 1-way hash for unique daily count, no raw IP stored

    def to_dict(self):
        return {
            'id': self.id,
            'page': self.page,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
