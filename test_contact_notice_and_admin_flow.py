"""
Automated Verification Suite for Contact Form Notice & Admin Dashboard-Only Flow
"""
import urllib.request, urllib.error, json, http.cookiejar
from unittest.mock import patch
from backend.services.portfolio_service import PortfolioService
from backend.models import db, Message
from backend.app import create_app
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:5000'

print("=== STARTING CONTACT NOTICE & ADMIN-ONLY DELIVERY TEST ===")


# 1. Static HTML & CSS Notice Verification

html_content = (BASE_DIR / 'frontend' / 'index.html').read_text(encoding='utf-8')
assert 'contact-admin-notice' in html_content
assert 'Please use your real mailbox to contact the owner' in html_content
assert "Your message will be received through the Admin Dashboard, not directly in the owner's email inbox." in html_content

# Confirm notice is located right before submit-btn
notice_idx = html_content.find('contact-admin-notice')
btn_idx = html_content.find('id="submit-btn"')
assert notice_idx != -1 and btn_idx != -1 and notice_idx < btn_idx, "Notice must appear directly above the Send Message button"

css_content = (BASE_DIR / 'frontend' / 'css' / 'style.css').read_text(encoding='utf-8')
assert '.contact-admin-notice' in css_content
assert '.notice-icon' in css_content
assert '.notice-header' in css_content
print("[PASS] 1. Static HTML and CSS notice elements confirmed in place.")


# 2. End-to-End Submission Flow (No SMTP Dispatch, Saved to DB)

app = create_app()
with app.app_context():
    # Verify no email sending is attempted
    with patch('backend.services.email_service.EmailService.send_contact_notification') as mock_email:
        # Submit contact message
        msg_dict = PortfolioService.submit_contact_message(
            name="Alice Walker",
            email="alice.walker@example.com",
            subject="Project Discussion",
            message="Hello Gopal, let us discuss your Computer Vision and Data Science work."
        )

        # 1. Verify NO email notification dispatched
        mock_email.assert_not_called()

        # 2. Verify message exists in DB
        db_msg = Message.query.filter_by(email="alice.walker@example.com").first()
        assert db_msg is not None
        assert db_msg.name == "Alice Walker"
        assert db_msg.subject == "Project Discussion"
        assert db_msg.is_read is False

        # Clean up test message
        db.session.delete(db_msg)
        db.session.commit()

print("[PASS] 2. Contact message submitted without SMTP dispatch and safely stored in DB.")

# 3. HTTP API & Admin Dashboard Inbox Verification

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 3a. Admin Login
login_payload = json.dumps({'email': Config.ADMIN_EMAIL, 'password': Config.ADMIN_DEFAULT_PASSWORD}).encode()
res = opener.open(urllib.request.Request(f"{BASE}/api/auth/login", data=login_payload, headers={'Content-Type': 'application/json'}))
assert json.loads(res.read())['success']

# 3b. Submit Public Contact Form via HTTP
contact_payload = json.dumps({
    'name': 'David Miller',
    'email': 'david.miller@example.com',
    'subject': 'Consulting Inquiry',
    'message': 'Looking for an experienced engineer in machine learning.'
}).encode('utf-8')

req = urllib.request.Request(
    f"{BASE}/api/public/contact",
    data=contact_payload,
    headers={'Content-Type': 'application/json'}
)
api_res = json.loads(urllib.request.urlopen(req).read())
assert api_res['success'] is True
assert 'Thank you' in api_res['message']
msg_id = api_res['data']['id']

# 3c. Verify Message Appears in Admin Messages Inbox
admin_msg_res = json.loads(opener.open(f"{BASE}/api/admin/messages").read())
assert admin_msg_res['success'] is True
found = any(m['id'] == msg_id and m['name'] == 'David Miller' for m in admin_msg_res['data'])
assert found, "Submitted message must appear in Admin Dashboard inbox"

# 3d. Clean up test message via Admin DELETE endpoint
del_req = urllib.request.Request(f"{BASE}/api/admin/messages/{msg_id}", method='DELETE')
del_res = json.loads(opener.open(del_req).read())
assert del_res['success'] is True

# 3e. Logout Admin
opener.open(urllib.request.Request(f"{BASE}/api/auth/logout", data=b'{}', headers={'Content-Type': 'application/json'}))

print("[PASS] 3. HTTP API and Admin Dashboard Inbox flow verified end-to-end.")

print("\n=== ALL CONTACT NOTICE & ADMIN DELIVERY TESTS PASSED ===")
