from datetime import datetime, timezone
from . import db

class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    # Hero & Identity Details
    greeting = db.Column(db.String(100), default="Hello, I'm")
    name = db.Column(db.String(150), default="Gopal Naik", nullable=False)
    title = db.Column(db.String(200), default="Computer Science & Engineering Student | Data Science")
    tagline = db.Column(db.String(300), default="I build data-driven applications and modern web solutions.")
    availability_status = db.Column(db.String(100), default="Available for Roles & Collaborations")
    
    # CTAs
    primary_cta_text = db.Column(db.String(50), default="View My Work →")
    primary_cta_url = db.Column(db.String(255), default="#projects")
    secondary_cta_text = db.Column(db.String(50), default="Contact Me")
    secondary_cta_url = db.Column(db.String(255), default="#contact")
    
    # Profile Visual
    profile_image = db.Column(db.String(255), default="/uploads/profile/gopal_profile.jpg")
    
    # About Section Details
    about_heading = db.Column(db.String(200), default="Turning Ideas Into Impactful Solutions")
    about_narrative = db.Column(db.Text, default="I'm a Computer Science & Engineering student specializing in Data Science. I enjoy building solutions that solve real-world problems using data, AI, and modern web technologies.")
    about_focus = db.Column(db.Text, default="Passionate about building full-stack architectures, computer vision and NLP models, and turning complex data streams into intuitive software solutions.")
    
    # 4 Customizable Factual Statistics
    stat_1_val = db.Column(db.String(50), default="4+")
    stat_1_label = db.Column(db.String(100), default="Projects Built")
    stat_2_val = db.Column(db.String(50), default="15+")
    stat_2_label = db.Column(db.String(100), default="Technologies & Tools")
    stat_3_val = db.Column(db.String(50), default="2026")
    stat_3_label = db.Column(db.String(100), default="Expected Graduation")
    stat_4_val = db.Column(db.String(50), default="Data Science")
    stat_4_label = db.Column(db.String(100), default="Specialization")

    # Contact Details
    email = db.Column(db.String(150), default="gopalnaik.dev@gmail.com")
    phone = db.Column(db.String(50), default="")
    location = db.Column(db.String(150), default="Open to Remote & On-Site")
    
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'greeting': self.greeting,
            'name': self.name,
            'title': self.title,
            'tagline': self.tagline,
            'availability_status': self.availability_status,
            'primary_cta_text': self.primary_cta_text,
            'primary_cta_url': self.primary_cta_url,
            'secondary_cta_text': self.secondary_cta_text,
            'secondary_cta_url': self.secondary_cta_url,
            'profile_image': self.profile_image,
            'about_heading': self.about_heading or "Turning Ideas Into Impactful Solutions",
            'about_narrative': self.about_narrative,
            'about_focus': self.about_focus,
            'stat_1_val': self.stat_1_val or "4+",
            'stat_1_label': self.stat_1_label or "Projects Built",
            'stat_2_val': self.stat_2_val or "15+",
            'stat_2_label': self.stat_2_label or "Technologies & Tools",
            'stat_3_val': self.stat_3_val or "2026",
            'stat_3_label': self.stat_3_label or "Expected Graduation",
            'stat_4_val': self.stat_4_val or "Data Science",
            'stat_4_label': self.stat_4_label or "Specialization",
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
