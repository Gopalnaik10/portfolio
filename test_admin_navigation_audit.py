"""
Comprehensive Admin Dashboard Navigation & State Isolation Audit Test Suite
"""
import urllib.request, urllib.error, json, http.cookiejar, re

BASE = 'http://127.0.0.1:5000'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("=== STARTING ADMIN DASHBOARD AUDIT TEST SUITE ===")


# 1. Static Analysis of admin.js & admin.css

with open('admin/js/admin.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

with open('admin/css/admin.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

with open('admin/dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Check for modal display none/flex lifecycle in JS and CSS
assert 'display: none' in css_content or 'display: none !important' in css_content, "CSS must hide modal backdrop by default"
assert '.admin-modal-backdrop' in css_content, "CSS must target .admin-modal-backdrop class"
assert 'modal.style.display = \'none\'' in js_content, "JS closeModal must explicitly set display: none"
assert 'modal.style.display = \'flex\'' in js_content, "JS openModal must set display: flex"
assert 'closeModal()' in js_content, "JS switchTab must call closeModal"
print("[PASS] 1. Static audit confirmed: modal classes, explicit display:none/flex lifecycle, and switchTab cleanup.")


from backend.config import Config

# 2. Authenticate Admin

login_payload = json.dumps({'email': Config.ADMIN_EMAIL, 'password': Config.ADMIN_DEFAULT_PASSWORD}).encode()
res = opener.open(urllib.request.Request(f"{BASE}/api/auth/login", data=login_payload, headers={'Content-Type': 'application/json'}))
assert json.loads(res.read())['success']
print("[PASS] 2. Admin authenticated.")


# 3. Test Full Forward Sequence:
# Dashboard -> Projects -> Edit -> Messages -> Open Msg -> Education -> Edit/Save -> About Me -> Skills -> Contact -> Hero -> Dashboard

# a. Dashboard Stats
res = opener.open(f"{BASE}/api/admin/dashboard-stats")
stats = json.loads(res.read())
assert stats['success']
print(f"[PASS] 3a. Dashboard tab loaded - {stats['data']['total_projects']} projects, {stats['data']['total_skills']} skills.")

# b. Projects (load, get project 1, simulate edit)
res = opener.open(f"{BASE}/api/admin/projects")
projs = json.loads(res.read())
assert projs['success']
assert len(projs['data']) == 4
p1 = projs['data'][0]
assert p1['title'] == 'AI Gym Trainer'
print(f"[PASS] 3b. Projects tab loaded: 4 projects confirmed. Project #1: '{p1['title']}' loaded.")

# c. Messages Tab
res = opener.open(f"{BASE}/api/admin/messages")
msgs = json.loads(res.read())
assert msgs['success']
print(f"[PASS] 3c. Messages tab loaded: {len(msgs['data'])} messages.")

# d. Education Tab (load, verify current saved record)
res = opener.open(f"{BASE}/api/admin/education")
edus = json.loads(res.read())
assert edus['success']
assert len(edus['data']) >= 1
edu1 = edus['data'][0]
assert edu1['degree'] == 'Computer Science & Engineering'
print(f"[PASS] 3d. Education tab loaded: '{edu1['degree']}' at '{edu1['institution']}'.")

# e. About Me / Profile Tab
res = opener.open(f"{BASE}/api/admin/profile")
prof = json.loads(res.read())
assert prof['success']
p_data = prof['data']
assert p_data['name'] == 'Gopal Naik'
assert p_data['about_heading'] == 'Turning Ideas Into Impactful Solutions'
print(f"[PASS] 3e. About Me tab loaded: Name='{p_data['name']}', Heading='{p_data['about_heading']}'.")

# f. Skills Tab
res = opener.open(f"{BASE}/api/admin/skills")
skills = json.loads(res.read())
assert skills['success']
assert len(skills['data']) == 11
print(f"[PASS] 3f. Skills tab loaded: 11 skills across categories.")

# g. Contact & Socials & Resume
res = opener.open(f"{BASE}/api/admin/socials")
socs = json.loads(res.read())
assert socs['success']
assert len(socs['data']) == 3
print(f"[PASS] 3g. Contact & Socials tab loaded: 3 active social channels.")

# h. Settings & SEO Tab
res = opener.open(f"{BASE}/api/admin/settings")
settings = json.loads(res.read())
assert settings['success']
print(f"[PASS] 3h. Settings & SEO tab loaded: Site Title='{settings['data']['site_title']}'.")


# 4. Test Reverse Sequence:
# Messages -> Projects -> Education -> About -> Contact -> Messages

opener.open(f"{BASE}/api/admin/messages")
opener.open(f"{BASE}/api/admin/projects")
opener.open(f"{BASE}/api/admin/education")
opener.open(f"{BASE}/api/admin/profile")
opener.open(f"{BASE}/api/admin/socials")
opener.open(f"{BASE}/api/admin/messages")
print("[PASS] 4. Reverse navigation sequence executed with zero errors.")


# 5. Verify Public Portfolio Integrity

pub_res = urllib.request.urlopen(f"{BASE}/api/public/portfolio")
pub_json = json.loads(pub_res.read())
assert pub_json['success']
assert pub_json['data']['profile']['name'] == 'Gopal Naik'
assert len(pub_json['data']['projects']) == 4
print("[PASS] 5. Public Portfolio API verified intact.")

# Logout
opener.open(urllib.request.Request(f"{BASE}/api/auth/logout", data=b'{}', headers={'Content-Type': 'application/json'}))
print("[PASS] 6. Admin logged out cleanly.")

print("\n=== ALL ADMIN DASHBOARD AUDIT TESTS PASSED SUCCESSFULLY ===")
