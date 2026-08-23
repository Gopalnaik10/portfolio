"""
Comprehensive verification of reality-based data & clean states.
Tests all 5 user-requested verification flows.
"""
import urllib.request, urllib.error, json, http.cookiejar, time

from backend.config import Config

BASE = 'http://127.0.0.1:5000'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("=== STARTING REALITY & ZERO-FAKE-DATA VERIFICATION ===")

# Test 1: Fresh Admin Login & Clean Initial State

login_payload = json.dumps({'email': Config.ADMIN_EMAIL, 'password': Config.ADMIN_DEFAULT_PASSWORD}).encode()
res = opener.open(urllib.request.Request(f"{BASE}/api/auth/login", data=login_payload, headers={'Content-Type': 'application/json'}))
login_data = json.loads(res.read())
assert login_data['success']
print(f"[PASS] 1. Admin login successful: {login_data['user']['email']}")

# Fetch initial dashboard stats
stats_res = opener.open(f"{BASE}/api/admin/dashboard-stats")
stats = json.loads(stats_res.read())['data']
print(f"       - Published Projects: {stats['published_projects']} (Total: {stats['total_projects']})")
print(f"       - Total Skills: {stats['total_skills']}")
print(f"       - Messages in Inbox: {stats['total_messages']}")
print(f"       - Recent Activity Count: {len(stats['recent_activities'])}")
assert stats['total_messages'] == 0, "Expected 0 messages in fresh DB"

# Verify messages inbox endpoint returns empty list
msgs_res = opener.open(f"{BASE}/api/admin/messages")
msgs = json.loads(msgs_res.read())['data']
assert len(msgs) == 0
print("[PASS] 1b. Verified Messages inbox has 0 fake records.")


# Test 2: Real Admin Activity Logging
# Edit an existing project (e.g. project 1)
proj_res = opener.open(f"{BASE}/api/admin/projects")
projs = json.loads(proj_res.read())['data']
proj1 = projs[0]

update_payload = json.dumps({
    'title': proj1['title'],
    'short_description': proj1['short_description']
}).encode()
opener.open(urllib.request.Request(f"{BASE}/api/admin/projects/{proj1['id']}", data=update_payload, method='PUT', headers={'Content-Type': 'application/json'}))

# Check History / Activity log
stats_res = opener.open(f"{BASE}/api/admin/dashboard-stats")
updated_stats = json.loads(stats_res.read())['data']
assert len(updated_stats['recent_activities']) > 0
latest_act = updated_stats['recent_activities'][0]
print(f"[PASS] 2. Real admin activity logged: \"{latest_act['description']}\" at {latest_act['formatted_time']}")

# Test 3: Real Contact Form Message
contact_payload = json.dumps({
    'name': 'Gopal Real Contact',
    'email': 'real.contact@example.com',
    'subject': 'Project Inquiry',
    'message': 'Hello Gopal, this is a real contact form submission.'
}).encode()
public_opener = urllib.request.build_opener()
public_res = public_opener.open(urllib.request.Request(f"{BASE}/api/public/contact", data=contact_payload, headers={'Content-Type': 'application/json'}))
assert json.loads(public_res.read())['success']

# Verify it appears in Admin Inbox
msgs_res = opener.open(f"{BASE}/api/admin/messages")
msgs = json.loads(msgs_res.read())['data']
assert len(msgs) == 1
assert msgs[0]['name'] == 'Gopal Real Contact'
print(f"[PASS] 3. Real contact message received in Admin Inbox: \"{msgs[0]['subject']}\" from {msgs[0]['name']}")

# Mark as read
opener.open(urllib.request.Request(f"{BASE}/api/admin/messages/{msgs[0]['id']}/read", data=b'{"is_read": true}', method='PUT', headers={'Content-Type': 'application/json'}))
# Delete it to keep DB clean
opener.open(urllib.request.Request(f"{BASE}/api/admin/messages/{msgs[0]['id']}", method='DELETE'))
print("       - Cleaned up verification message.")

# Test 4: Real Visitor Tracking
# Public portfolio visit
v_before = updated_stats['total_visits']
public_opener.open(f"{BASE}/api/public/portfolio")
stats_res = opener.open(f"{BASE}/api/admin/dashboard-stats")
v_after = json.loads(stats_res.read())['data']['total_visits']
assert v_after > v_before
print(f"[PASS] 4. Real visitor tracking confirmed: Visits incremented ({v_before} -> {v_after})")

# Test 5: Logout
opener.open(urllib.request.Request(f"{BASE}/api/auth/logout", data=b'{}', headers={'Content-Type': 'application/json'}))
print("[PASS] 5. Admin session logged out cleanly.")

print("\n=== ALL 5 REALITY VERIFICATION TESTS PASSED PERFECTLY ===")
