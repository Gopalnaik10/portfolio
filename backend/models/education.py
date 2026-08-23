from datetime import datetime, timezone
import json
from . import db

class Education(db.Model):
    __tablename__ = 'education'

    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(200), default="Data Science")
    institution = db.Column(db.String(200), nullable=False)
    start_year = db.Column(db.String(20), default="202X")
    end_year = db.Column(db.String(20), default="202X")
    expected_graduation = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, default="")
    coursework = db.Column(db.String(500), default="Data Structures, Algorithms, Machine Learning")
    published = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_coursework_list(self):
        if not self.coursework:
            return []
        try:
            parsed = json.loads(self.coursework)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, TypeError):
            pass
        return [c.strip() for c in self.coursework.split(',') if c.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'degree': self.degree,
            'specialization': self.specialization,
            'institution': self.institution,
            'start_year': self.start_year,
            'end_year': self.end_year,
            'expected_graduation': self.expected_graduation,
            'description': self.description,
            'coursework': self.get_coursework_list(),
            'coursework_raw': self.coursework,
            'published': self.published,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
