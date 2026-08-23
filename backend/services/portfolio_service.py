import os
import json
from pathlib import Path
from datetime import datetime, timezone
from backend.models import (
    db, Profile, Skill, Project, Education, SocialLink, 
    Resume, Message, SiteSettings, ActivityLog, AnalyticsVisit
)
from backend.services.email_service import EmailService
from backend.config import Config

class PortfolioService:
    @staticmethod
    def get_public_portfolio_data():
        """Aggregates all published portfolio data for public visitors."""
        profile = Profile.query.first()
        settings = SiteSettings.query.first()
        resume = Resume.query.filter_by(is_active=True).order_by(Resume.uploaded_at.desc()).first()

        # Validate physical resume file on disk
        if resume:
            file_rel = resume.filename.lstrip('/')
            file_path = Config.BASE_DIR / file_rel
            if not file_path.exists() or not file_path.is_file():
                try:
                    db.session.delete(resume)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                resume = None

        # 1. Fetch enabled skills grouped by category
        skills = Skill.query.filter_by(enabled=True).order_by(Skill.display_order.asc(), Skill.id.asc()).all()
        categories_dict = {}
        for s in skills:
            if s.category not in categories_dict:
                categories_dict[s.category] = []
            categories_dict[s.category].append(s.to_dict())

        # 2. Fetch published projects
        projects = Project.query.filter_by(published=True).order_by(Project.display_order.asc(), Project.id.desc()).all()
        project_categories = sorted(list(set(p.category for p in projects if p.category)))

        # 3. Fetch published education
        education = Education.query.filter_by(published=True).order_by(Education.display_order.asc(), Education.id.asc()).all()

        # 4. Fetch enabled social links
        socials = SocialLink.query.filter_by(enabled=True).order_by(SocialLink.display_order.asc(), SocialLink.id.asc()).all()

        return {
            'settings': settings.to_dict() if settings else {},
            'profile': profile.to_dict() if profile else {},
            'skill_categories': categories_dict,
            'projects': [p.to_dict() for p in projects],
            'project_categories': project_categories,
            'education': [e.to_dict() for e in education],
            'social_links': [s.to_dict() for s in socials],
            'resume': resume.to_dict() if resume else None
        }

    @staticmethod
    def get_admin_dashboard_stats():
        total_projects = Project.query.count()
        published_projects = Project.query.filter_by(published=True).count()
        total_skills = Skill.query.count()
        unread_messages = Message.query.filter_by(is_read=False).count()
        total_messages = Message.query.count()
        active_resume = Resume.query.filter_by(is_active=True).first()
        total_visits = AnalyticsVisit.query.count()

        recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(8).all()
        popular_projects = Project.query.order_by(Project.view_count.desc()).limit(5).all()

        return {
            'total_projects': total_projects,
            'published_projects': published_projects,
            'total_skills': total_skills,
            'unread_messages': unread_messages,
            'total_messages': total_messages,
            'active_resume': active_resume.to_dict() if active_resume else None,
            'total_visits': total_visits,
            'recent_activities': [a.to_dict() for a in recent_activities],
            'popular_projects': [p.to_dict() for p in popular_projects]
        }

    # Profile Management
    @staticmethod
    def update_profile(data: dict):
        profile = Profile.query.first()
        if not profile:
            profile = Profile()
            db.session.add(profile)

        for field in [
            'greeting', 'name', 'title', 'tagline', 'availability_status',
            'primary_cta_text', 'primary_cta_url', 'secondary_cta_text', 'secondary_cta_url',
            'profile_image', 'about_heading', 'about_narrative', 'about_focus',
            'stat_1_val', 'stat_1_label', 'stat_2_val', 'stat_2_label',
            'stat_3_val', 'stat_3_label', 'stat_4_val', 'stat_4_label',
            'email', 'phone', 'location'
        ]:
            if field in data:
                setattr(profile, field, data[field])

        db.session.add(ActivityLog(
            action_type="PROFILE_UPDATED",
            description=f"Profile / About Me information updated"
        ))
        db.session.commit()
        return profile.to_dict()

    # Skills Management
    @staticmethod
    def get_all_skills():
        skills = Skill.query.order_by(Skill.display_order.asc(), Skill.id.asc()).all()
        return [s.to_dict() for s in skills]

    @staticmethod
    def add_skill(data: dict):
        highest_order = db.session.query(db.func.max(Skill.display_order)).scalar() or 0
        skill = Skill(
            category=data.get('category', 'Core Languages').strip(),
            name=data.get('name', '').strip(),
            icon=data.get('icon', 'code').strip(),
            enabled=bool(data.get('enabled', True)),
            display_order=int(data.get('display_order', highest_order + 1))
        )
        db.session.add(skill)
        db.session.add(ActivityLog(
            action_type="SKILL_ADDED",
            description=f"Added skill: {skill.name} in {skill.category}"
        ))
        db.session.commit()
        return skill.to_dict()

    @staticmethod
    def update_skill(skill_id: int, data: dict):
        skill = Skill.query.get(skill_id)
        if not skill:
            return None
        if 'category' in data: skill.category = data['category'].strip()
        if 'name' in data: skill.name = data['name'].strip()
        if 'icon' in data: skill.icon = data['icon'].strip()
        if 'enabled' in data: skill.enabled = bool(data['enabled'])
        if 'display_order' in data: skill.display_order = int(data['display_order'])
        
        db.session.commit()
        return skill.to_dict()

    @staticmethod
    def delete_skill(skill_id: int):
        skill = Skill.query.get(skill_id)
        if not skill:
            return False
        name = skill.name
        db.session.delete(skill)
        db.session.add(ActivityLog(
            action_type="SKILL_DELETED",
            description=f"Deleted skill: {name}"
        ))
        db.session.commit()
        return True

    @staticmethod
    def reorder_skills(ordered_ids: list):
        for index, item_id in enumerate(ordered_ids):
            skill = Skill.query.get(item_id)
            if skill:
                skill.display_order = index + 1
        db.session.commit()
        return True

    # Projects Management
    @staticmethod
    def get_all_projects_admin():
        projects = Project.query.order_by(Project.display_order.asc(), Project.id.desc()).all()
        return [p.to_dict() for p in projects]

    @staticmethod
    def add_project(data: dict):
        highest_order = db.session.query(db.func.max(Project.display_order)).scalar() or 0
        tech_str = data.get('technologies', '')
        if isinstance(tech_str, list):
            tech_str = ", ".join(tech_str)

        features = data.get('key_features', '')
        if isinstance(features, list):
            features = json.dumps(features)

        project = Project(
            title=data.get('title', '').strip(),
            category=data.get('category', 'Machine Learning').strip(),
            short_description=data.get('short_description', '').strip(),
            description=data.get('description', '').strip(),
            problem_statement=data.get('problem_statement', '').strip(),
            key_features=features,
            technologies=tech_str,
            image=data.get('image', '/assets/project-placeholder.svg').strip(),
            github_url=data.get('github_url', '').strip(),
            live_url=data.get('live_url', '').strip(),
            featured=bool(data.get('featured', False)),
            published=bool(data.get('published', True)),
            display_order=int(data.get('display_order', highest_order + 1))
        )
        db.session.add(project)
        db.session.add(ActivityLog(
            action_type="PROJECT_ADDED",
            description=f"Created new project: {project.title}"
        ))
        db.session.commit()
        return project.to_dict()

    @staticmethod
    def update_project(project_id: int, data: dict):
        project = Project.query.get(project_id)
        if not project:
            return None

        if 'title' in data: project.title = data['title'].strip()
        if 'category' in data: project.category = data['category'].strip()
        if 'short_description' in data: project.short_description = data['short_description'].strip()
        if 'description' in data: project.description = data['description'].strip()
        if 'problem_statement' in data: project.problem_statement = data['problem_statement'].strip()
        if 'key_features' in data:
            kf = data['key_features']
            project.key_features = json.dumps(kf) if isinstance(kf, list) else str(kf)
        if 'technologies' in data:
            tech = data['technologies']
            project.technologies = ", ".join(tech) if isinstance(tech, list) else str(tech)
        if 'image' in data: project.image = data['image'].strip()
        if 'github_url' in data: project.github_url = data['github_url'].strip()
        if 'live_url' in data: project.live_url = data['live_url'].strip()
        if 'featured' in data: project.featured = bool(data['featured'])
        if 'published' in data: project.published = bool(data['published'])
        if 'display_order' in data: project.display_order = int(data['display_order'])

        db.session.add(ActivityLog(
            action_type="PROJECT_UPDATED",
            description=f"Updated project: {project.title}"
        ))
        db.session.commit()
        return project.to_dict()

    @staticmethod
    def delete_project(project_id: int):
        project = Project.query.get(project_id)
        if not project:
            return False
        title = project.title
        db.session.delete(project)
        db.session.add(ActivityLog(
            action_type="PROJECT_DELETED",
            description=f"Deleted project: {title}"
        ))
        db.session.commit()
        return True

    @staticmethod
    def reorder_projects(ordered_ids: list):
        for index, item_id in enumerate(ordered_ids):
            project = Project.query.get(item_id)
            if project:
                project.display_order = index + 1
        db.session.commit()
        return True

    @staticmethod
    def record_project_view(project_id: int):
        project = Project.query.get(project_id)
        if project:
            project.view_count += 1
            db.session.commit()
            return project.view_count
        return 0

    # Education Management
    @staticmethod
    def get_all_education_admin():
        records = Education.query.order_by(Education.display_order.asc(), Education.id.asc()).all()
        return [r.to_dict() for r in records]

    @staticmethod
    def add_education(data: dict):
        highest_order = db.session.query(db.func.max(Education.display_order)).scalar() or 0
        cw = data.get('coursework', '')
        if isinstance(cw, list): cw = ", ".join(cw)

        edu = Education(
            degree=data.get('degree', '').strip(),
            specialization=data.get('specialization', '').strip(),
            institution=data.get('institution', '').strip(),
            start_year=data.get('start_year', '').strip(),
            end_year=data.get('end_year', '').strip(),
            expected_graduation=bool(data.get('expected_graduation', False)),
            description=data.get('description', '').strip(),
            coursework=cw,
            published=bool(data.get('published', True)),
            display_order=int(data.get('display_order', highest_order + 1))
        )
        db.session.add(edu)
        db.session.add(ActivityLog(
            action_type="EDUCATION_ADDED",
            description=f"Added education: {edu.degree} at {edu.institution}"
        ))
        db.session.commit()
        return edu.to_dict()

    @staticmethod
    def update_education(edu_id: int, data: dict):
        edu = Education.query.get(edu_id)
        if not edu:
            return None
        if 'degree' in data: edu.degree = data['degree'].strip()
        if 'specialization' in data: edu.specialization = data['specialization'].strip()
        if 'institution' in data: edu.institution = data['institution'].strip()
        if 'start_year' in data: edu.start_year = data['start_year'].strip()
        if 'end_year' in data: edu.end_year = data['end_year'].strip()
        if 'expected_graduation' in data: edu.expected_graduation = bool(data['expected_graduation'])
        if 'description' in data: edu.description = data['description'].strip()
        if 'coursework' in data:
            cw = data['coursework']
            edu.coursework = ", ".join(cw) if isinstance(cw, list) else str(cw)
        if 'published' in data: edu.published = bool(data['published'])
        if 'display_order' in data: edu.display_order = int(data['display_order'])

        db.session.commit()
        return edu.to_dict()

    @staticmethod
    def delete_education(edu_id: int):
        edu = Education.query.get(edu_id)
        if not edu:
            return False
        deg = edu.degree
        db.session.delete(edu)
        db.session.add(ActivityLog(
            action_type="EDUCATION_DELETED",
            description=f"Deleted education: {deg}"
        ))
        db.session.commit()
        return True

    @staticmethod
    def reorder_education(ordered_ids: list):
        for index, item_id in enumerate(ordered_ids):
            edu = Education.query.get(item_id)
            if edu:
                edu.display_order = index + 1
        db.session.commit()
        return True

    # Social Links Management
    @staticmethod
    def get_all_socials():
        socials = SocialLink.query.order_by(SocialLink.display_order.asc(), SocialLink.id.asc()).all()
        return [s.to_dict() for s in socials]

    @staticmethod
    def add_social(data: dict):
        highest_order = db.session.query(db.func.max(SocialLink.display_order)).scalar() or 0
        social = SocialLink(
            name=data.get('name', '').strip(),
            url=data.get('url', '').strip(),
            icon=data.get('icon', 'link').strip(),
            enabled=bool(data.get('enabled', True)),
            display_order=int(data.get('display_order', highest_order + 1))
        )
        db.session.add(social)
        db.session.commit()
        return social.to_dict()

    @staticmethod
    def update_social(social_id: int, data: dict):
        social = SocialLink.query.get(social_id)
        if not social:
            return None
        if 'name' in data: social.name = data['name'].strip()
        if 'url' in data: social.url = data['url'].strip()
        if 'icon' in data: social.icon = data['icon'].strip()
        if 'enabled' in data: social.enabled = bool(data['enabled'])
        if 'display_order' in data: social.display_order = int(data['display_order'])
        db.session.commit()
        return social.to_dict()

    @staticmethod
    def delete_social(social_id: int):
        social = SocialLink.query.get(social_id)
        if not social:
            return False
        db.session.delete(social)
        db.session.commit()
        return True

    # Resume Management
    @staticmethod
    def set_active_resume(filename: str, original_filename: str, file_size: int):
        # Deactivate previous active resumes
        Resume.query.update({'is_active': False})
        resume = Resume(
            filename=filename,
            original_filename=original_filename,
            file_size=file_size,
            is_active=True
        )
        db.session.add(resume)
        db.session.add(ActivityLog(
            action_type="RESUME_UPLOADED",
            description=f"Uploaded new resume: {original_filename}"
        ))
        db.session.commit()
        return resume.to_dict()

    @staticmethod
    def get_active_resume():
        resume = Resume.query.filter_by(is_active=True).order_by(Resume.uploaded_at.desc()).first()
        if resume:
            file_rel = resume.filename.lstrip('/')
            file_path = Config.BASE_DIR / file_rel
            if not file_path.exists() or not file_path.is_file():
                try:
                    db.session.delete(resume)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                return None
        return resume

    @staticmethod
    def delete_resume(resume_id: int):
        resume = Resume.query.get(resume_id)
        if not resume:
            # Check if there are any orphaned active records
            orphans = Resume.query.all()
            for o in orphans:
                file_rel = o.filename.lstrip('/')
                file_path = Config.BASE_DIR / file_rel
                try:
                    if file_path.exists() and file_path.is_file():
                        file_path.unlink()
                except Exception:
                    pass
                db.session.delete(o)
            db.session.commit()
            return True, "No resume record found; cleaned up stale state."

        orig_filename = resume.original_filename
        file_rel = resume.filename.lstrip('/')
        file_path = Config.BASE_DIR / file_rel

        # 1. Delete physical file from storage
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
        except Exception as e:
            return False, f"Failed to delete resume file from storage: {str(e)}"

        # 2. Verify physical file no longer exists
        if file_path.exists():
            return False, "Resume file could not be unlinked from storage."

        # 3. Log activity
        db.session.add(ActivityLog(
            action_type="RESUME_DELETED",
            description=f"Permanently deleted resume: {orig_filename}"
        ))

        # 4. Remove database record
        db.session.delete(resume)
        db.session.commit()
        return True, "Resume deleted successfully from storage and database."

    @staticmethod
    def delete_active_resume():
        resumes = Resume.query.all()
        if not resumes:
            return True, "No active resumes to delete."

        for r in resumes:
            file_rel = r.filename.lstrip('/')
            file_path = Config.BASE_DIR / file_rel
            try:
                if file_path.exists() and file_path.is_file():
                    file_path.unlink()
            except Exception:
                pass
            db.session.delete(r)

        db.session.add(ActivityLog(
            action_type="RESUME_DELETED",
            description="Permanently deleted active resume and storage files."
        ))
        db.session.commit()
        return True, "All resume files and records removed successfully."

    # Messages Management
    @staticmethod
    def submit_contact_message(name: str, email: str, subject: str, message: str):
        msg = Message(
            name=name.strip(),
            email=email.strip(),
            subject=subject.strip(),
            message=message.strip(),
            is_read=False
        )
        db.session.add(msg)
        db.session.add(ActivityLog(
            action_type="MESSAGE_RECEIVED",
            description=f"New message from {name} ({email}): {subject}"
        ))
        db.session.commit()
        # Messages are received and managed exclusively through the Admin Dashboard
        return msg.to_dict()

    @staticmethod
    def get_all_messages():
        messages = Message.query.order_by(Message.created_at.desc()).all()
        return [m.to_dict() for m in messages]

    @staticmethod
    def mark_message_read(msg_id: int, is_read: bool = True):
        msg = Message.query.get(msg_id)
        if not msg:
            return None
        msg.is_read = is_read
        db.session.commit()
        return msg.to_dict()

    @staticmethod
    def delete_message(msg_id: int):
        msg = Message.query.get(msg_id)
        if not msg:
            return False
        db.session.delete(msg)
        db.session.commit()
        return True

    # Site Settings & Maintenance
    @staticmethod
    def get_settings():
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)
            db.session.commit()
        return settings.to_dict()

    @staticmethod
    def update_settings(data: dict):
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)

        for field in ['site_title', 'meta_description', 'keywords', 'og_image', 'maintenance_mode', 'maintenance_message']:
            if field in data:
                setattr(settings, field, data[field])

        db.session.add(ActivityLog(
            action_type="SETTINGS_UPDATED",
            description=f"Site & SEO settings updated"
        ))
        db.session.commit()
        return settings.to_dict()

    # Backup & Restore
    @staticmethod
    def export_full_backup():
        """Exports non-sensitive portfolio database records to a JSON format."""
        profile = Profile.query.first()
        skills = Skill.query.all()
        projects = Project.query.all()
        education = Education.query.all()
        socials = SocialLink.query.all()
        settings = SiteSettings.query.first()

        backup_payload = {
            'version': '1.0',
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'profile': profile.to_dict() if profile else {},
            'skills': [s.to_dict() for s in skills],
            'projects': [p.to_dict() for p in projects],
            'education': [e.to_dict() for e in education],
            'social_links': [s.to_dict() for s in socials],
            'settings': settings.to_dict() if settings else {}
        }
        return backup_payload

    @staticmethod
    def restore_from_backup(payload: dict):
        """Restores portfolio content from a validated JSON backup."""
        if not isinstance(payload, dict):
            return False, "Invalid backup format"

        # Restore Profile
        if 'profile' in payload and isinstance(payload['profile'], dict):
            profile = Profile.query.first() or Profile()
            for k, v in payload['profile'].items():
                if hasattr(profile, k) and k not in ('id', 'updated_at'):
                    setattr(profile, k, v)
            db.session.add(profile)

        # Restore Skills
        if 'skills' in payload and isinstance(payload['skills'], list):
            Skill.query.delete()
            for s in payload['skills']:
                skill = Skill(
                    category=s.get('category', 'Core Languages'),
                    name=s.get('name', ''),
                    icon=s.get('icon', 'code'),
                    enabled=s.get('enabled', True),
                    display_order=s.get('display_order', 0)
                )
                db.session.add(skill)

        # Restore Projects
        if 'projects' in payload and isinstance(payload['projects'], list):
            Project.query.delete()
            for p in payload['projects']:
                tech = p.get('technologies_raw') or p.get('technologies', '')
                if isinstance(tech, list): tech = ", ".join(tech)
                proj = Project(
                    title=p.get('title', ''),
                    category=p.get('category', 'Machine Learning'),
                    short_description=p.get('short_description', ''),
                    description=p.get('description', ''),
                    technologies=tech,
                    image=p.get('image', '/assets/project-placeholder.svg'),
                    github_url=p.get('github_url', ''),
                    live_url=p.get('live_url', ''),
                    featured=p.get('featured', False),
                    published=p.get('published', True),
                    display_order=p.get('display_order', 0)
                )
                db.session.add(proj)

        # Restore Education
        if 'education' in payload and isinstance(payload['education'], list):
            Education.query.delete()
            for e in payload['education']:
                cw = e.get('coursework_raw') or e.get('coursework', '')
                if isinstance(cw, list): cw = ", ".join(cw)
                edu = Education(
                    degree=e.get('degree', ''),
                    specialization=e.get('specialization', ''),
                    institution=e.get('institution', ''),
                    start_year=e.get('start_year', ''),
                    end_year=e.get('end_year', ''),
                    expected_graduation=e.get('expected_graduation', False),
                    description=e.get('description', ''),
                    coursework=cw,
                    published=e.get('published', True),
                    display_order=e.get('display_order', 0)
                )
                db.session.add(edu)

        # Restore Social Links
        if 'social_links' in payload and isinstance(payload['social_links'], list):
            SocialLink.query.delete()
            for sl in payload['social_links']:
                social = SocialLink(
                    name=sl.get('name', ''),
                    url=sl.get('url', ''),
                    icon=sl.get('icon', 'link'),
                    enabled=sl.get('enabled', True),
                    display_order=sl.get('display_order', 0)
                )
                db.session.add(social)

        # Restore Settings
        if 'settings' in payload and isinstance(payload['settings'], dict):
            settings = SiteSettings.query.first() or SiteSettings()
            for k, v in payload['settings'].items():
                if hasattr(settings, k) and k not in ('id', 'updated_at'):
                    setattr(settings, k, v)
            db.session.add(settings)

        db.session.add(ActivityLog(
            action_type="BACKUP_RESTORED",
            description=f"Restored portfolio database from JSON backup"
        ))
        db.session.commit()
        return True, "Portfolio data restored successfully"
