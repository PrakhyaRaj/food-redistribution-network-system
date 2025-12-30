import requests
import json

BASE = "http://127.0.0.1:5000"

LOGIN = BASE + "/auth/login"
NOTIFS = BASE + "/api/mongodb/notifications"

creds = {"email": "rajesh@ex.com", "password": "password"}

s = requests.Session()
resp = s.post(LOGIN, json=creds)
print("login status", resp.status_code)
print(resp.text)
if resp.status_code != 200:
    raise SystemExit("Login failed")

token = resp.json().get('access_token')
headers = {"Authorization": f"Bearer {token}"}

r = s.get(NOTIFS, headers=headers)
print("notifications status", r.status_code)
print(r.text)
