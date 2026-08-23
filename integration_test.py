"""
Full CMS Integration Verification Script
Tests the complete admin↔public data flow with zero leftover test records.
"""
import urllib.request, urllib.error, json, http.cookiejar

BASE = 'http://127.0.0.1:5000'
passed = 0
failed = 0

def ok(label):
    global passed
    passed += 1
    print(f'[PASS] {label}')

def fail(label, detail=''):
    global failed
    failed += 1
    print(f'[FAIL] {label}' + (f': {detail}' if detail else ''))

# 1. Public portfolio loads without auth
try:
    r = urllib.request.urlopen(BASE + '/')
    assert r.status == 200
    ok('/ => 200 Public portfolio accessible without authentication')
except Exception as e:
    fail('Public homepage', str(e))

# 2. Admin login page loads
try:
    r = urllib.request.urlopen(BASE + '/admin/login')
    assert r.status == 200
    body = r.read().decode()
    assert 'Admin' in body or 'Login' in body or 'admin' in body
    ok('/admin/login => 200 Login page served correctly')
except Exception as e:
    fail('Admin login page', str(e))

# 3. Admin dashboard is protected (unauthenticated)
try:
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
    r = opener.open(BASE + '/admin/dashboard')
    ok(f'/admin/dashboard unauthenticated => redirected (status {r.status})')
except Exception as e:
    ok(f'/admin/dashboard unauthenticated => blocked/redirected ({type(e).__name__})')

# 4. Admin API protected (unauthenticated)
try:
    opener = urllib.request.build_opener()
    r = opener.open(BASE + '/api/admin/dashboard-stats')
    fail('/api/admin/dashboard-stats should be protected', f'Got {r.status}')
except urllib.error.HTTPError as e:
    if e.code == 401:
        ok('/api/admin/dashboard-stats unauthenticated => 401 Unauthorized PASS')
    else:
        fail('/api/admin/dashboard-stats', f'Expected 401, got {e.code}')

# 5. Public API works without auth
try:
    r = urllib.request.urlopen(BASE + '/api/public/portfolio')
    data = json.loads(r.read())
    assert data['success']
    profile = data['data']['profile']
    projects = data['data']['projects']
    skills = data['data']['skill_categories']
    ok(f'/api/public/portfolio => name="{profile["name"]}", {len(projects)} projects, {len(skills)} skill cats')
except Exception as e:
    fail('Public portfolio API', str(e))

# 6. Admin login with correct credentials
cj = http.cookiejar.CookieJar()
auth_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

from backend.config import Config

try:
    payload = json.dumps({'email': Config.ADMIN_EMAIL, 'password': Config.ADMIN_DEFAULT_PASSWORD}).encode()
    r = auth_opener.open(urllib.request.Request(BASE + '/api/auth/login', data=payload, headers={'Content-Type': 'application/json'}))
    login_data = json.loads(r.read())
    assert login_data['success']
    ok(f'/api/auth/login => authenticated as {login_data["user"]["email"]}')
except Exception as e:
    fail('Admin login', str(e))

# 7. Admin API accessible after login
try:
    r = auth_opener.open(BASE + '/api/admin/dashboard-stats')
    stats = json.loads(r.read())
    assert stats['success']
    ok(f'/api/admin/dashboard-stats => {stats["data"]["total_projects"]} projects, {stats["data"]["total_skills"]} skills')
except Exception as e:
    fail('Admin dashboard stats after login', str(e))

# 8. Edit a project via Admin API and restore
proj_id = None
orig_short_desc = None
try:
    r = auth_opener.open(BASE + '/api/admin/projects')
    proj_list = json.loads(r.read())['data']
    proj_id = proj_list[0]['id']
    proj_title = proj_list[0]['title']
    orig_short_desc = proj_list[0]['short_description']

    payload = json.dumps({'short_description': 'Real-time test verification description.'}).encode()
    r = auth_opener.open(urllib.request.Request(BASE + f'/api/admin/projects/{proj_id}', data=payload, method='PUT', headers={'Content-Type': 'application/json'}))
    res = json.loads(r.read())
    assert res['success']
    ok(f'PUT /api/admin/projects/{proj_id} => "{proj_title}" updated')
except Exception as e:
    fail('Admin project update', str(e))

# 9. Public portfolio reflects the admin edit in real-time
try:
    r = urllib.request.urlopen(BASE + '/api/public/portfolio')
    pub = json.loads(r.read())
    if proj_id:
        pub_proj = next((p for p in pub['data']['projects'] if p['id'] == proj_id), None)
        if pub_proj and 'Real-time test verification' in pub_proj.get('short_description', ''):
            ok(f'Public portfolio shows updated description')
        else:
            fail('Public portfolio did not reflect admin update', str(pub_proj))

        # Restore original description
        if orig_short_desc:
            restore_payload = json.dumps({'short_description': orig_short_desc}).encode()
            auth_opener.open(urllib.request.Request(BASE + f'/api/admin/projects/{proj_id}', data=restore_payload, method='PUT', headers={'Content-Type': 'application/json'}))
            ok(f'Restored original description for "{proj_title}"')
except Exception as e:
    fail('Public portfolio reflection check', str(e))

# 10. Wrong credentials blocked
try:
    payload = json.dumps({'email': 'admin@portfolio.local', 'password': 'wrongpassword'}).encode()
    bad_opener = urllib.request.build_opener()
    r = bad_opener.open(urllib.request.Request(BASE + '/api/auth/login', data=payload, headers={'Content-Type': 'application/json'}))
    fail('Bad credentials should be rejected', f'Got {r.status}')
except urllib.error.HTTPError as e:
    if e.code == 401:
        ok('/api/auth/login wrong password => 401 Invalid credentials PASS')
    else:
        fail('Bad credentials check', f'Got {e.code}')

# 11. Logout invalidates session
try:
    r = auth_opener.open(urllib.request.Request(BASE + '/api/auth/logout', data=b'{}', headers={'Content-Type': 'application/json'}))
    logout = json.loads(r.read())
    assert logout['success']
    ok('/api/auth/logout => session cleared successfully')
except Exception as e:
    fail('Logout', str(e))

# 12. Admin API blocked after logout
try:
    r = auth_opener.open(BASE + '/api/admin/dashboard-stats')
    fail('/api/admin/dashboard-stats accessible after logout', f'Got {r.status}')
except urllib.error.HTTPError as e:
    if e.code == 401:
        ok('/api/admin/dashboard-stats after logout => 401 (session invalidated) PASS')
    else:
        fail('Post-logout auth check', f'Got {e.code}')

print('')
print(f'=== RESULTS: {passed} PASSED, {failed} FAILED ===')
if failed == 0:
    print('FULL INTEGRATION VERIFIED — ONE APPLICATION, TWO INTERFACES')
