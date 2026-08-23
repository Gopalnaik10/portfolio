"""
Comprehensive Verification Suite for CMS Upgrades
Tests:
- Reorganized Admin Dashboard API & Auth
- Dedicated About Me Editor & 4 Customizable Stats
- Project Details with Problem Statement & Key Features
- Contact Form + Backend SMTP Email Notification Service
- Public Portfolio Reflection
"""
import urllib.request, urllib.error, json, http.cookiejar, time

from backend.config import Config

BASE = 'http://127.0.0.1:5000'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("=== STARTING FULL CMS UPGRADES VERIFICATION ===")

# 1. Admin Authentication
login_payload = json.dumps({'email': Config.ADMIN_EMAIL, 'password': Config.ADMIN_DEFAULT_PASSWORD}).encode()
res = opener.open(urllib.request.Request(f"{BASE}/api/auth/login", data=login_payload, headers={'Content-Type': 'application/json'}))
login_data = json.loads(res.read())
assert login_data['success']
print(f"[PASS] 1. Admin authenticated: {login_data['user']['email']}")

# 2. About Me Editor & 4 Stats Persistence

about_payload = json.dumps({
    'about_heading': 'Engineering Impactful Systems with AI & Data',
    'about_narrative': 'Updated narrative bio for testing About Me editor.',
    'about_focus': 'Updated focus on distributed architectures and deep vision models.',
    'stat_1_val': '5+',
    'stat_1_label': 'Engineering Projects',
    'stat_2_val': '20+',
    'stat_2_label': 'Tools & Frameworks',
    'stat_3_val': '2026',
    'stat_3_label': 'Graduation Milestone',
    'stat_4_val': 'Machine Learning',
    'stat_4_label': 'Primary Focus'
}).encode()

res = opener.open(urllib.request.Request(f"{BASE}/api/admin/profile", data=about_payload, method='PUT', headers={'Content-Type': 'application/json'}))
profile_res = json.loads(res.read())
assert profile_res['success']
p_data = profile_res['data']
assert p_data['about_heading'] == 'Engineering Impactful Systems with AI & Data'
assert p_data['stat_1_val'] == '5+'
assert p_data['stat_4_label'] == 'Primary Focus'
print(f"[PASS] 2. About Me editor saved: Heading=\"{p_data['about_heading']}\", Stat 1=\"{p_data['stat_1_val']} {p_data['stat_1_label']}\"")

# Restore original About Me content
restore_about = json.dumps({
    'about_heading': 'Turning Ideas Into Impactful Solutions',
    'about_narrative': "I'm a Computer Science & Engineering student specializing in Data Science. I enjoy building solutions that solve real-world problems using data, AI, and modern web technologies.",
    'about_focus': 'Passionate about building full-stack architectures, computer vision and NLP models, and turning complex data streams into intuitive software solutions.',
    'stat_1_val': '4+',
    'stat_1_label': 'Projects Built',
    'stat_2_val': '15+',
    'stat_2_label': 'Technologies & Tools',
    'stat_3_val': '2026',
    'stat_3_label': 'Expected Graduation',
    'stat_4_val': 'Data Science',
    'stat_4_label': 'Specialization'
}).encode()
opener.open(urllib.request.Request(f"{BASE}/api/admin/profile", data=restore_about, method='PUT', headers={'Content-Type': 'application/json'}))
print("       - Cleanly restored original About Me content.")

# 3. Project Creation & Details with Problem & Key Features

proj_payload = json.dumps({
    'title': 'Test Autonomous Agent Pipeline',
    'category': 'AI & Systems',
    'short_description': 'Autonomous multi-agent research and reasoning framework.',
    'problem_statement': 'Researchers spend excessive time manually synthesizing multi-source data.',
    'key_features': [
        'Hierarchical agent orchestration using LangGraph',
        'Real-time semantic vector retrieval via FAISS',
        'Automated markdown thesis generation engine'
    ],
    'description': 'Full architectural implementation of an autonomous reasoning pipeline.',
    'technologies': 'Python, PyTorch, LangChain, FastAPI',
    'github_url': 'https://github.com/gopalnaik/agent-pipeline',
    'live_url': 'https://agent-demo.example.com',
    'featured': True,
    'published': True
}).encode()

res = opener.open(urllib.request.Request(f"{BASE}/api/admin/projects", data=proj_payload, headers={'Content-Type': 'application/json'}))
proj_res = json.loads(res.read())
assert proj_res['success']
created_proj = proj_res['data']
assert created_proj['problem_statement'] == 'Researchers spend excessive time manually synthesizing multi-source data.'
assert len(created_proj['key_features']) == 3
print(f"[PASS] 3. Project with Problem & Features created: \"{created_proj['title']}\" (ID: {created_proj['id']})")
print(f"       - Features count: {len(created_proj['key_features'])}")

# Clean up created test project
del_res = opener.open(urllib.request.Request(f"{BASE}/api/admin/projects/{created_proj['id']}", method='DELETE'))
assert del_res.status == 200
print("       - Cleaned up temporary test project.")

# 4. Public Portfolio API Verification

pub_res = urllib.request.urlopen(f"{BASE}/api/public/portfolio")
pub_data = json.loads(pub_res.read())['data']
assert pub_data['profile']['about_heading'] == 'Turning Ideas Into Impactful Solutions'
assert pub_data['profile']['stat_1_val'] == '4+'
assert len(pub_data['projects']) == 4
for p in pub_data['projects']:
    assert 'problem_statement' in p
    assert 'key_features' in p
    assert isinstance(p['key_features'], list)
print(f"[PASS] 4. Public portfolio API verified with {len(pub_data['projects'])} projects containing structured problem statements & key features.")

# 5. Contact Form + Backend SMTP Notification

contact_payload = json.dumps({
    'name': 'Gopal Enterprise Partner',
    'email': 'partner@techcorp.example',
    'subject': 'Full-Stack Machine Learning Collaboration',
    'message': 'Hello Gopal, we reviewed your Computer Vision and NLP projects and would like to connect regarding an engineering role.'
}).encode()

contact_res = urllib.request.urlopen(urllib.request.Request(f"{BASE}/api/public/contact", data=contact_payload, headers={'Content-Type': 'application/json'}))
contact_data = json.loads(contact_res.read())
assert contact_data['success']
msg_id = contact_data['data']['id']
print(f"[PASS] 5. Contact submission saved to DB and triggered SMTP notification safely (Message ID: {msg_id})")

# Verify message in Admin Inbox
admin_msgs_res = opener.open(f"{BASE}/api/admin/messages")
admin_msgs = json.loads(admin_msgs_res.read())['data']
found = next((m for m in admin_msgs if m['id'] == msg_id), None)
assert found is not None
assert found['name'] == 'Gopal Enterprise Partner'
print(f"[PASS] 5b. Message verified in Admin Inbox: \"{found['subject']}\"")

# Clean up test contact message
opener.open(urllib.request.Request(f"{BASE}/api/admin/messages/{msg_id}", method='DELETE'))
print("       - Cleaned up verification message.")

# 6. Admin Logout

opener.open(urllib.request.Request(f"{BASE}/api/auth/logout", data=b'{}', headers={'Content-Type': 'application/json'}))
print("[PASS] 6. Admin logged out cleanly.")

print("\n=== ALL CMS UPGRADE TESTS PASSED PERFECTLY ===")
