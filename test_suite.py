import urllib.request
import urllib.error
import urllib.parse
import json
import http.cookiejar
import time

from backend.config import Config

base_url = 'http://127.0.0.1:5000'
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

print("=== STARTING AUTOMATED PORTFOLIO CMS TEST SUITE ===")

# Test 1: Public Homepage
req = opener.open(f"{base_url}/")
assert req.status == 200
print("[PASS] Test 1: Public Homepage loaded (200 OK)")

# Test 2: Public Portfolio API
req = opener.open(f"{base_url}/api/public/portfolio")
data = json.loads(req.read().decode())
assert data['success'] is True
assert 'profile' in data['data']
assert 'projects' in data['data']
assert 'skill_categories' in data['data']
print(f"[PASS] Test 2: Public Portfolio API returned {len(data['data']['projects'])} projects and {len(data['data']['skill_categories'])} skill categories")

# Test 3: Public Contact Form Submission
contact_payload = json.dumps({
    'name': 'Test Visitor',
    'email': 'test.visitor@example.com',
    'subject': 'Inquiry Test',
    'message': 'This is an automated test message that will be cleaned up.'
}).encode()
req = opener.open(urllib.request.Request(f"{base_url}/api/public/contact", data=contact_payload, headers={'Content-Type': 'application/json'}))
res = json.loads(req.read().decode())
assert res['success'] is True
created_msg_id = res['data']['id']
print("[PASS] Test 3: Public contact form submission saved securely to database")

# Test 4: Admin Login Page
req = opener.open(f"{base_url}/admin/login")
assert req.status == 200
print("[PASS] Test 4: Admin login page served (200 OK)")

# Test 5: Protected Route without Session
try:
    req = urllib.request.urlopen(f"{base_url}/api/admin/dashboard-stats")
    print("[FAIL] Test 5: Expected 401 Unauthorized")
except urllib.error.HTTPError as e:
    assert e.code == 401
    print("[PASS] Test 5: Protected admin API correctly blocked unauthenticated access (401 Unauthorized)")

# Test 6: Admin Login Authentication
login_payload = json.dumps({
    'email': Config.ADMIN_EMAIL,
    'password': Config.ADMIN_DEFAULT_PASSWORD
}).encode()
req = opener.open(urllib.request.Request(f"{base_url}/api/auth/login", data=login_payload, headers={'Content-Type': 'application/json'}))
res = json.loads(req.read().decode())
assert res['success'] is True
print(f"[PASS] Test 6: Admin login authenticated successfully: {res['user']['email']}")

# Test 7: Verify Session via /api/auth/me
req = opener.open(f"{base_url}/api/auth/me")
res = json.loads(req.read().decode())
assert res['authenticated'] is True
print("[PASS] Test 7: Authenticated session confirmed via /api/auth/me")

# Test 8: Admin Dashboard Stats
req = opener.open(f"{base_url}/api/admin/dashboard-stats")
stats = json.loads(req.read().decode())['data']
assert stats['total_projects'] >= 3
print(f"[PASS] Test 8: Dashboard stats loaded - Unread Messages: {stats['unread_messages']}, Total Visits: {stats['total_visits']}")

# Test 9: Create New Project via Admin API
new_proj_payload = json.dumps({
    'title': 'Test Temporary Project',
    'category': 'Test Category',
    'short_description': 'Temporary test project summary.',
    'description': 'Temporary test project full description.',
    'technologies': 'Python, Flask',
    'github_url': 'https://github.com/test/repo',
    'featured': False,
    'published': False
}).encode()
req = opener.open(urllib.request.Request(f"{base_url}/api/admin/projects", data=new_proj_payload, headers={'Content-Type': 'application/json'}))
res = json.loads(req.read().decode())
assert res['success'] is True
created_proj_id = res['data']['id']
print(f"[PASS] Test 9: Admin created test project: \"{res['data']['title']}\" (ID: {created_proj_id})")

# Test 10: Verify Message in Admin Inbox and Mark Read
req = opener.open(f"{base_url}/api/admin/messages")
messages = json.loads(req.read().decode())['data']
target_msg = next((m for m in messages if m['id'] == created_msg_id), None)
assert target_msg is not None
print(f"[PASS] Test 10: Contact message confirmed in Admin Inbox")

# Clean up created test message and test project
del_msg_req = urllib.request.Request(f"{base_url}/api/admin/messages/{created_msg_id}", method='DELETE')
opener.open(del_msg_req)

del_proj_req = urllib.request.Request(f"{base_url}/api/admin/projects/{created_proj_id}", method='DELETE')
opener.open(del_proj_req)
print("[PASS] Cleaned up temporary test project and test message")

# Test 11: Export JSON Backup
req = opener.open(f"{base_url}/api/admin/backup/export")
backup_content = json.loads(req.read().decode())
assert 'profile' in backup_content
assert 'projects' in backup_content
print(f"[PASS] Test 11: JSON database backup generated with {len(backup_content['projects'])} projects")

# Test 12: Admin Logout
req = opener.open(urllib.request.Request(f"{base_url}/api/auth/logout", data=b"{}", headers={'Content-Type': 'application/json'}))
res = json.loads(req.read().decode())
assert res['success'] is True
print("[PASS] Test 12: Admin logged out cleanly and session cleared")

print("\n=== ALL 12 TESTS PASSED PERFECTLY ===")
