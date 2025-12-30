# 🔐 Postman Authentication Guide

## Problem: 403 Unauthorized Error

**Root Cause**: JWT token is missing or invalid in the Authorization header.

---

## ✅ Quick Fix (3 Steps)

### Step 1: Register/Login to Get Token

**POST** `http://localhost:5000/auth/register`

```json
{
  "email": "test@example.com",
  "password": "Test@1234",
  "name": "Test User",
  "phone": "1234567890",
  "location_lat": 40.7128,
  "location_long": -74.0060,
  "roles": ["receiver"]
}
```

**Response** (copy the `access_token`):
```json
{
  "success": true,
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "user_id": 1,
  "message": "User registered successfully"
}
```

---

### Step 2: Add Token to Authorization Header

In Postman:

1. Click **Authorization** tab
2. Select **Bearer Token** from dropdown
3. Paste the `access_token` value

**Or manually add header**:
```
Authorization: Bearer eyJhbGc...
```

---

### Step 3: Test Transaction Endpoint

**GET** `http://localhost:5000/api/mongodb/transactions`

**Headers**:
```
Authorization: Bearer eyJhbGc...
```

**Expected Response** (200 OK):
```json
{
  "success": true,
  "transactions": [],
  "stats": {
    "donations_made": 0,
    "items_received": 0,
    "completed_count": 0,
    "active_count": 0,
    "success_rate": 0
  },
  "count": 0
}
```

---

## 🔧 Common Issues & Fixes

### Issue 1: "No authorization token provided"
**Solution**: Add `Authorization: Bearer <token>` header

### Issue 2: "Invalid token" or "Signature verification failed"
**Solutions**:
- Get a new token (Step 1 above)
- Make sure you copied the entire token
- Check `JWT_SECRET_KEY` environment variable matches on server
- Restart the Flask server after changing JWT_SECRET_KEY

### Issue 3: Token expired
**Solution**: Use the `refresh_token` to get a new access token:

**POST** `http://localhost:5000/auth/refresh`

**Headers**:
```
Authorization: Bearer <refresh_token>
```

**Response**:
```json
{
  "access_token": "new_token_here"
}
```

---

## 📋 All MongoDB Endpoints (Require JWT)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/mongodb/transactions` | Get all user transactions |
| GET | `/api/mongodb/transactions/<id>` | Get specific transaction |
| PUT | `/api/mongodb/transactions/<id>/update-status` | Update transaction status |
| GET | `/api/mongodb/route-optimizations/<request_id>` | Get route data |
| GET | `/api/mongodb/notifications/<user_id>` | Get notifications |
| GET | `/api/mongodb/feedback/user/<user_id>` | Get user feedback |
| GET | `/api/mongodb/activities/<user_id>` | Get activity log |

**All require**: `Authorization: Bearer <access_token>` header

---

## 📱 Postman Collection Template

Save this as a `.json` file and import into Postman:

```json
{
  "info": {
    "name": "FRNS API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Register User",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"email\": \"test@example.com\", \"password\": \"Test@1234\", \"name\": \"Test User\", \"phone\": \"1234567890\", \"location_lat\": 40.7128, \"location_long\": -74.0060, \"roles\": [\"receiver\"]}"
        },
        "url": {
          "raw": "http://localhost:5000/auth/register",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["auth", "register"]
        }
      }
    },
    {
      "name": "Get Transactions",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "url": {
          "raw": "http://localhost:5000/api/mongodb/transactions",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "mongodb", "transactions"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "access_token",
      "value": ""
    }
  ]
}
```

**How to use**:
1. Import this collection into Postman
2. Run "Register User" endpoint
3. Copy the `access_token` from response
4. In Postman top menu, click "Variables"
5. Paste token into `access_token` variable
6. Now all requests will use `{{access_token}}`

---

## 🚀 Quick Copy-Paste

### cURL Example (with valid token)

```bash
curl -X GET "http://localhost:5000/api/mongodb/transactions" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Python Example

```python
import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

response = requests.get("http://localhost:5000/api/mongodb/transactions", headers=headers)
print(response.json())
```

### JavaScript/Fetch Example

```javascript
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

fetch("http://localhost:5000/api/mongodb/transactions", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## ✅ Checklist

- [ ] Server running on `http://localhost:5000`
- [ ] Registered a test user
- [ ] Copied `access_token` from registration response
- [ ] Added `Authorization: Bearer <token>` header
- [ ] Endpoint returns 200 OK with data
- [ ] Token is valid (not expired)

If you still get 403:
1. Check Flask server is running (`python app.py`)
2. Get a fresh token from `/auth/register`
3. Make sure `JWT_SECRET_KEY` is set in `.env`
4. Restart Flask server
5. Try again with fresh token

---

**Still having issues?** Check the Flask console output for error messages when the request comes in.
