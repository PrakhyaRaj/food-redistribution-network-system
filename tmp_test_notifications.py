import requests
import json
BASE='http://localhost:5000'
creds={'email':'rajesh@ex.com','password':'password123'}
try:
    r = requests.post(BASE+'/auth/login', json=creds, timeout=5)
    print('login status', r.status_code)
    data = r.json()
    token = data.get('access_token')
    uid = data.get('user_id')
    print('user_id from login:', uid)
    headers={'Authorization': f'Bearer {token}'}
    resp = requests.get(f"{BASE}/api/mongodb/notifications/{uid}", headers=headers, timeout=5)
    print('notifications status', resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)
except Exception as e:
    print('error', e)
