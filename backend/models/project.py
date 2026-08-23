from datetime import datetime, timezone
import json
from . import db

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), default="Machine Learning", nullable=False)
    short_description = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, default="")
    problem_statement = db.Column(db.Text, default="")
    key_features = db.Column(db.Text, default="") # JSON list or newline-separated list
    technologies = db.Column(db.String(300), default="Python, Scikit-Learn") # Comma-separated or JSON list
    image = db.Column(db.String(255), default="/assets/project-placeholder.svg")
    github_url = db.Column(db.String(255), default="https://github.com/yourusername")
    live_url = db.Column(db.String(255), default="")
    featured = db.Column(db.Boolean, default=False, nullable=False)
    published = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def get_tech_list(self):
        if not self.technologies:
            return []
        try:
            parsed = json.loads(self.technologies)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, TypeError):
            pass
        return [t.strip() for t in self.technologies.split(',') if t.strip()]

    def get_features_list(self):
        if not self.key_features:
            return []
        try:
            parsed = json.loads(self.key_features)
            if isinstance(parsed, list):
                return [str(f).strip() for f in parsed if str(f).strip()]
        except (ValueError, TypeError):
            pass
        # Fallback: split by newlines or bullet points
        lines = [line.strip().lstrip('•-* ').strip() for line in self.key_features.split('\n') if line.strip()]
        return lines

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'short_description': self.short_description,
            'description': self.description or self.short_description,
            'problem_statement': self.problem_statement or "",
            'key_features': self.get_features_list(),
            'key_features_raw': self.key_features or "",
            'technologies': self.get_tech_list(),
            'technologies_raw': self.technologies,
            'image': self.image,
            'github_url': self.github_url,
            'live_url': self.live_url,
            'featured': self.featured,
            'published': self.published,
            'display_order': self.display_order,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
