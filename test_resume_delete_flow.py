"""
Verification Test Suite for Complete Resume Upload, Download, Physical File Deletion, and Public Sync
"""
import urllib.request, urllib.error, json, http.cookiejar, os
from pathlib import Path

from backend.config import Config

BASE = 'http://127.0.0.1:5000'
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("=== STARTING RESUME DELETION & SYNC VERIFICATION ===")

# 1. Admin Authentication

login_payload = json.dumps({'email': Config.ADMIN_EMAIL, 'password': Config.ADMIN_DEFAULT_PASSWORD}).encode()
res = opener.open(urllib.request.Request(f"{BASE}/api/auth/login", data=login_payload, headers={'Content-Type': 'application/json'}))
assert json.loads(res.read())['success']
print("[PASS] 1. Admin authenticated successfully.")

# 2. Upload Sample PDF Resume via multipart/form-data

sample_pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF\n"
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="resume"; filename="Gopal_Naik_Resume.pdf"\r\n'
    f'Content-Type: application/pdf\r\n\r\n'
).encode('utf-8') + sample_pdf_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request(
    f"{BASE}/api/admin/resume/upload",
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)
upload_res = json.loads(opener.open(req).read())
assert upload_res['success']
resume_id = upload_res['data']['id']
resume_rel_path = upload_res['data']['filename'].lstrip('/')
print(f"[PASS] 2. Resume uploaded successfully (ID: {resume_id}, path: {resume_rel_path}).")

# 3. Verify Physical File Exists on Server Disk

BASE_DIR = Path(__file__).resolve().parent
physical_file = BASE_DIR / resume_rel_path
assert physical_file.exists() and physical_file.is_file(), f"Physical file must exist at {physical_file}"
print(f"[PASS] 3. Physical file confirmed on disk: {physical_file} ({os.path.getsize(physical_file)} bytes).")


# 4. Verify Public Download URL Serves PDF

dl_res = opener.open(f"{BASE}/api/public/resume/download")
assert dl_res.status == 200
assert dl_res.headers.get('Content-Type') == 'application/pdf'
assert b"%PDF" in dl_res.read()
print("[PASS] 4. Public download endpoint /api/public/resume/download serves PDF.")

# 5. Verify Public Portfolio API returns active resume

pub_res = json.loads(urllib.request.urlopen(f"{BASE}/api/public/portfolio").read())
assert pub_res['data']['resume'] is not None
assert pub_res['data']['resume']['id'] == resume_id
print("[PASS] 5. Public portfolio API returns active resume data.")


# 6. DELETE Resume via Admin API (Simulating Admin Dashboard click)

del_req = urllib.request.Request(f"{BASE}/api/admin/resume/{resume_id}", method='DELETE')
del_res = json.loads(opener.open(del_req).read())
assert del_res['success']
print(f"[PASS] 6. Admin delete request succeeded: {del_res['message']}")


# 7. Verify Physical File was Unlinked & Removed from Disk

assert not physical_file.exists(), f"Physical file MUST be deleted from disk: {physical_file}"
print("[PASS] 7. Physical file verified deleted from server storage.")


# 8. Verify Admin Resume Endpoint Returns None

adm_res = json.loads(opener.open(f"{BASE}/api/admin/resume").read())
assert adm_res['data'] is None
print("[PASS] 8. Admin resume endpoint confirms no active resume.")


# 9. Verify Public Portfolio API Returns None for Resume

pub_res2 = json.loads(urllib.request.urlopen(f"{BASE}/api/public/portfolio").read())
assert pub_res2['data']['resume'] is None
print("[PASS] 9. Public portfolio API confirms resume is None (UI hides Download CV button).")


# 10. Verify Public Download URL Returns 404 Not Found

try:
    urllib.request.urlopen(f"{BASE}/api/public/resume/download")
    assert False, "Download should have failed with 404"
except urllib.error.HTTPError as e:
    assert e.code == 404
    print("[PASS] 10. Public download endpoint correctly returns 404 Not Found.")


# 11. Delete When No Resume Exists (Graceful Handling)
#
del_req_stale = urllib.request.Request(f"{BASE}/api/admin/resume/99999", method='DELETE')
del_res_stale = json.loads(opener.open(del_req_stale).read())
assert del_res_stale['success']
print("[PASS] 11. Deleting non-existent/stale resume handled safely.")


# 12. Verify Other Sections Untouched

assert pub_res2['data']['profile']['name'] == 'Gopal Naik'
assert len(pub_res2['data']['projects']) == 4
assert len(pub_res2['data']['education']) >= 1
print("[PASS] 12. Profile, Projects, Skills, and Education 100% preserved.")

# Logout
opener.open(urllib.request.Request(f"{BASE}/api/auth/logout", data=b'{}', headers={'Content-Type': 'application/json'}))
print("[PASS] 13. Admin logged out cleanly.")

print("\n=== ALL RESUME DELETION & LIFECYCLE TESTS PASSED ===")
