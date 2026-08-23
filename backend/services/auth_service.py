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

        if not user.check_password(current_password):
            return False, "Current password is incorrect"

        if len(new_password) < 8:
            return False, "New password must be at least 8 characters long"

        user.set_password(new_password)
        db.session.add(ActivityLog(
            action_type="PASSWORD_CHANGED",
            description=f"Admin password was changed"
        ))
        db.session.commit()
        return True, "Password successfully updated"
