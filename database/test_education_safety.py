"""
Verification Suite for Education Background Editor & Non-Destructive Database Safety Policy
"""
import urllib.request, urllib.error, json, http.cookiejar

from backend.config import Config

BASE = 'http://127.0.0.1:5000'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("=== STARTING EDUCATION EDITOR & DATA SAFETY VERIFICATION ===")


# 1. Admin Authentication

login_payload = json.dumps({'email': Config.ADMIN_EMAIL, 'password': Config.ADMIN_DEFAULT_PASSWORD}).encode()
res = opener.open(urllib.request.Request(f"{BASE}/api/auth/login", data=login_payload, headers={'Content-Type': 'application/json'}))
assert json.loads(res.read())['success']
print("[PASS] 1. Admin authenticated successfully.")


# 2. Get Current Education Data

res = opener.open(f"{BASE}/api/admin/education")
edu_data = json.loads(res.read())
assert edu_data['success']
assert len(edu_data['data']) >= 1
initial_edu = edu_data['data'][0]
edu_id = initial_edu['id']
print(f"[PASS] 2. Loaded current education record (ID: {edu_id}):")
print(f"       Degree: {initial_edu['degree']}")
print(f"       Institution: {initial_edu['institution']}")
print(f"       Specialization: {initial_edu['specialization']}")
print(f"       Coursework: {initial_edu['coursework']}")


# 3. Update Education Background via API (simulating editor save)

update_payload = json.dumps({
    'degree': 'Bachelor of Engineering in Computer Science',
    'specialization': 'Specialization in Data Science & Artificial Intelligence',
    'institution': 'University Department of Computer Science & Engineering',
    'start_year': '2022',
    'end_year': '2026',
    'expected_graduation': True,
    'description': 'Advanced academic focus on Deep Learning, Statistical Machine Learning, and Distributed Cloud Computing.',
    'coursework': 'Data Structures & Algorithms, Machine Learning, Deep Neural Networks, Cloud Computing, Database Management Systems',
    'published': True
}).encode()

res = opener.open(urllib.request.Request(f"{BASE}/api/admin/education/{edu_id}", data=update_payload, method='PUT', headers={'Content-Type': 'application/json'}))
updated_res = json.loads(res.read())
assert updated_res['success']
updated_edu = updated_res['data']
assert updated_edu['degree'] == 'Bachelor of Engineering in Computer Science'
assert updated_edu['institution'] == 'University Department of Computer Science & Engineering'
print(f"[PASS] 3. Education background updated and persisted in DB (ID: {edu_id}).")

# 4. Public Portfolio API Verification

pub_res = urllib.request.urlopen(f"{BASE}/api/public/portfolio")
pub_json = json.loads(pub_res.read())
assert pub_json['success']
pub_edu = pub_json['data']['education'][0]
assert pub_edu['degree'] == 'Bachelor of Engineering in Computer Science'
assert pub_edu['institution'] == 'University Department of Computer Science & Engineering'
print("[PASS] 4. Public portfolio API reflects updated education record.")

# 5. Verify Unrelated Data is 100% Preserved
pub_data = pub_json['data']
assert pub_data['profile']['name'] == 'Gopal Naik'
assert pub_data['profile']['about_heading'] == 'Turning Ideas Into Impactful Solutions'
assert len(pub_data['projects']) == 4
for p in pub_data['projects']:
    assert len(p['problem_statement']) > 0
    assert len(p['key_features']) > 0
print(f"[PASS] 5. Unrelated data perfectly preserved: Profile=\"{pub_data['profile']['name']}\", 4 Projects with problem statements & features.")

# 6. Restore Original Education Record
restore_payload = json.dumps({
    'degree': initial_edu['degree'],
    'specialization': initial_edu['specialization'],
    'institution': initial_edu['institution'],
    'start_year': initial_edu['start_year'],
    'end_year': initial_edu['end_year'],
    'expected_graduation': initial_edu['expected_graduation'],
    'description': initial_edu['description'],
    'coursework': initial_edu['coursework_raw'],
    'published': initial_edu['published']
}).encode()

opener.open(urllib.request.Request(f"{BASE}/api/admin/education/{edu_id}", data=restore_payload, method='PUT', headers={'Content-Type': 'application/json'}))
print(f"[PASS] 6. Original Education record restored cleanly.")

# 7. Admin Logout
opener.open(urllib.request.Request(f"{BASE}/api/auth/logout", data=b'{}', headers={'Content-Type': 'application/json'}))
print("[PASS] 7. Admin logged out cleanly.")

print("\n=== ALL EDUCATION & DATA SAFETY TESTS PASSED ===")
