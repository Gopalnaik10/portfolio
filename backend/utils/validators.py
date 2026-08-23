import re
from typing import Tuple, Optional

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def validate_email_address(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_contact_message(data: dict) -> Tuple[bool, Optional[str]]:
    if not data or not isinstance(data, dict):
        return False, "Invalid request payload"

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not name or len(name) < 2:
        return False, "Name must be at least 2 characters long"
    if not validate_email_address(email):
        return False, "Please provide a valid email address"
    if not subject or len(subject) < 2:
        return False, "Subject must be at least 2 characters long"
    if not message or len(message) < 5:
        return False, "Message must be at least 5 characters long"

    return True, None

def validate_allowed_extension(filename: str, allowed_extensions: set) -> bool:
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions
