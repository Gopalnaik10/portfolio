from flask import session
from backend.models import db, AdminUser, ActivityLog

class AuthService:
    @staticmethod
    def login(email: str, password: str) -> tuple[bool, str, dict]:
        if not email or not password:
            return False, "Email and password are required", {}

        admin = AdminUser.query.filter_by(email=email.strip().lower()).first()
        if not admin or not admin.check_password(password):
            return False, "Invalid email or password", {}

        session['admin_id'] = admin.id
        session['admin_email'] = admin.email
        session.permanent = True

        # Log login activity
        db.session.add(ActivityLog(
            action_type="ADMIN_LOGIN",
            description=f"Admin logged in ({admin.email})"
        ))
        db.session.commit()

        return True, "Login successful", admin.to_dict()

    @staticmethod
    def logout() -> bool:
        admin_id = session.get('admin_id')
        if admin_id:
            admin = AdminUser.query.get(admin_id)
            if admin:
                db.session.add(ActivityLog(
                    action_type="ADMIN_LOGOUT",
                    description=f"Admin logged out ({admin.email})"
                ))
                db.session.commit()

        session.clear()
        return True

    @staticmethod
    def get_current_user() -> AdminUser:
        admin_id = session.get('admin_id')
        if not admin_id:
            return None
        return AdminUser.query.get(admin_id)

    @staticmethod
    def change_password(current_password: str, new_password: str) -> tuple[bool, str]:
        user = AuthService.get_current_user()
        if not user:
            return False, "Authentication session expired"

        if not current_password:
            return False, "Current password is required"

        if not user.check_password(current_password):
            return False, "Current password is incorrect"

        if not new_password or len(new_password) < 8:
            return False, "New password must be at least 8 characters long"

        user.set_password(new_password)
        db.session.add(ActivityLog(
            action_type="PASSWORD_CHANGED",
            description=f"Admin password was changed"
        ))
        db.session.commit()
        return True, "Password successfully updated"

    @staticmethod
    def change_email(current_password: str, new_email: str) -> tuple[bool, str, dict]:
        user = AuthService.get_current_user()
        if not user:
            return False, "Authentication session expired", {}

        if not current_password:
            return False, "Current password is required to verify identity", {}

        if not user.check_password(current_password):
            return False, "Current password is incorrect", {}

        from backend.utils.validators import validate_email_address
        clean_email = (new_email or '').strip().lower()
        if not clean_email or not validate_email_address(clean_email):
            return False, "Please provide a valid email address", {}

        # Prevent duplicate email conflict
        existing = AdminUser.query.filter(AdminUser.email == clean_email, AdminUser.id != user.id).first()
        if existing:
            return False, "This email address is already in use", {}

        old_email = user.email
        user.email = clean_email
        session['admin_email'] = clean_email

        db.session.add(ActivityLog(
            action_type="ADMIN_EMAIL_CHANGED",
            description=f"Admin email updated from {old_email} to {clean_email}"
        ))
        db.session.commit()
        return True, "Email successfully updated", user.to_dict()

    @staticmethod
    def update_credentials(current_password: str, new_email: str = None, new_password: str = None) -> tuple[bool, str, dict]:
        user = AuthService.get_current_user()
        if not user:
            return False, "Authentication session expired", {}

        if not current_password:
            return False, "Current password is required to verify identity", {}

        if not user.check_password(current_password):
            return False, "Current password is incorrect", {}

        from backend.utils.validators import validate_email_address
        changes_made = []

        # Handle Email Update
        if new_email:
            clean_email = new_email.strip().lower()
            if clean_email != user.email:
                if not validate_email_address(clean_email):
                    return False, "Please provide a valid email address", {}
                existing = AdminUser.query.filter(AdminUser.email == clean_email, AdminUser.id != user.id).first()
                if existing:
                    return False, "This email address is already in use", {}
                old_email = user.email
                user.email = clean_email
                session['admin_email'] = clean_email
                changes_made.append("email")

        # Handle Password Update
        if new_password:
            if len(new_password) < 8:
                return False, "New password must be at least 8 characters long", {}
            user.set_password(new_password)
            changes_made.append("password")

        if not changes_made:
            return False, "No changes were specified", {}

        log_desc = f"Admin credentials updated ({', '.join(changes_made)})"
        db.session.add(ActivityLog(
            action_type="CREDENTIALS_UPDATED",
            description=log_desc
        ))
        db.session.commit()

        if "email" in changes_made and "password" in changes_made:
            msg = "Email and password successfully updated"
        elif "email" in changes_made:
            msg = "Admin email successfully updated"
        else:
            msg = "Password successfully updated"

        return True, msg, user.to_dict()
