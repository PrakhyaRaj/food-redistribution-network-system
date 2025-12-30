# ✅ Step-by-Step Guide to Fix 403 Error & Test Everything

## Phase 1: Get Your Token (1 minute)

### Step 1.1: Open PowerShell
```powershell
# You should already be in the project directory
cd "c:\Users\Prakhya Raj\OneDrive\Desktop\FRNS\food-redistribution-network-system"
```

### Step 1.2: Run the Token Generator
```powershell
python troubleshoot.py
```

### Step 1.3: Wait for Output
You'll see:
```
✅ API Status: 200
✅ User registered successfully!
   Email: test@example.com
   User ID: 13

📋 Token (save this):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MT...
✅ Authentication successful!
✅ Transactions endpoint working!
```

### Step 1.4: Copy the Token
- Highlight the entire long token string (starts with `eyJhbGc`)
- Copy it (Ctrl+C)
- Save to notepad or keep terminal open

---

## Phase 2: Configure Postman (2 minutes)

### Step 2.1: Open Postman
- Launch Postman application
- Create a new request or use an existing one

### Step 2.2: Set Up Authorization
1. Click the **Authorization** tab
2. From the dropdown at the top, select **Bearer Token**
3. In the **Token** field, paste your token (right-click → paste)
4. Leave everything else as is

**Visual Guide:**
```
┌─ Authorization Tab ─────────────────┐
│ Type: Bearer Token ▼                │
│                                     │
│ Token:                              │
│ [eyJhbGciOiJIUzI1NiIsInR5cCI0J...] │
│                                     │
└─────────────────────────────────────┘
```

### Step 2.3: Verify Token is Set
- Look at the **Headers** tab
- You should see a new header automatically added:
  ```
  Authorization: Bearer eyJhbGc...
  ```

---

## Phase 3: Test a Single Endpoint (1 minute)

### Step 3.1: Create Test Request
1. In Postman, create a **new request**
2. Set method to **GET**
3. Enter URL: `http://localhost:5000/api/mongodb/transactions`

**Form should look like:**
```
[GET] http://localhost:5000/api/mongodb/transactions

Params | Headers | Authorization | Body | ...
                    ▲ (Token added here)
```

### Step 3.2: Send Request
1. Click the **Send** button
2. Wait for response

### Step 3.3: Check Response
You should see:

**Status: 200 OK** ✅

**Response body:**
```json
{
  "success": true,
  "transactions": [],
  "stats": {
    "total_donations": 0,
    "total_received": 0,
    "completed_donations": 0,
    "completed_received": 0
  },
  "count": 0
}
```

**If you see this → SUCCESS!** 🎉

---

## Phase 4: Test All Endpoints (2 minutes)

### Step 4.1: Test Authentication Endpoint
**Request:**
```
GET http://localhost:5000/api/mongodb/test-auth
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "JWT authentication working!",
  "user_id": "13",
  "user_email": "test@example.com",
  "mongo_status": "connected"
}
```

### Step 4.2: Test API Status (No Token Needed)
**Request:**
```
GET http://localhost:5000/api/mongodb/status
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "api": "running",
  "mongodb": "connected"
}
```

### Step 4.3: Test Other Endpoints (All Need Token)
Try these with the same token:

**Get User Feedback:**
```
GET http://localhost:5000/api/mongodb/feedback/user/13
```

**Get Activities:**
```
GET http://localhost:5000/api/mongodb/activities/13
```

**Get Notifications:**
```
GET http://localhost:5000/api/mongodb/notifications/13
```

---

## Phase 5: Optional - Import Postman Collection (3 minutes)

### Step 5.1: Download Collection
- File already exists: `FRNS_API_Postman_Collection.json`
- Location: Project root directory

### Step 5.2: Import in Postman
1. Click **File** menu
2. Select **Import**
3. Choose **Upload Files**
4. Select `FRNS_API_Postman_Collection.json`
5. Click **Import**

### Step 5.3: Use Pre-configured Requests
1. You'll see a new collection called "FRNS API"
2. Click "Register User" request
3. Click **Send**
4. Token automatically saved to environment
5. All other requests now have token pre-filled

---

## Phase 6: Troubleshooting

### Issue: "No Authorization Token Provided"
**Solution:**
- Token not in Authorization header
- Fix: Go to **Authorization** tab → **Bearer Token** → paste token

### Issue: "Token has expired"
**Solution:**
- Run `python troubleshoot.py` again
- Get new token
- Update in Postman

### Issue: "MongoDB not available" (Status 503)
**Solution:**
- This is OK! API still works with PostgreSQL
- MongoDB is optional for this phase
- All data is still stored and retrievable

### Issue: Still Getting 403?
**Checklist:**
- [ ] Token pasted in **Authorization** tab (not Headers)
- [ ] Dropdown set to **Bearer Token**
- [ ] Full token pasted (it's very long)
- [ ] Flask server running (`python app.py` in backend)
- [ ] Token from recent `troubleshoot.py` run

---

## Complete Checklist

### ✅ Setup Phase
- [ ] PowerShell open in project directory
- [ ] `python troubleshoot.py` runs successfully
- [ ] Token generated and visible
- [ ] Token copied

### ✅ Postman Phase
- [ ] Postman open
- [ ] Authorization tab → Bearer Token selected
- [ ] Token pasted in Token field
- [ ] Headers tab shows Authorization header

### ✅ Testing Phase
- [ ] GET /api/mongodb/transactions returns 200 OK
- [ ] GET /api/mongodb/test-auth returns 200 OK
- [ ] GET /api/mongodb/status returns 200 OK
- [ ] Response has "success": true
- [ ] All checks pass

### ✅ Final Phase
- [ ] Token works for all endpoints
- [ ] Understand how JWT authentication works
- [ ] Can add token to any request
- [ ] Ready to integrate with frontend

---

## Next: Integration with Frontend

Once all tests pass:

1. **Add MatchedFoods Component**
   - File: `frontend/src/components/requests/MatchedFoods.tsx`
   - Add to request detail page
   - Pass request ID as prop

2. **Add TransactionHistory Component**
   - File: `frontend/src/components/mongodb/TransactionHistory.tsx`
   - Add to dashboard
   - Will fetch transactions automatically

3. **Add ProfileFeedback Component**
   - File: `frontend/src/components/profile/ProfileFeedback.tsx`
   - Add to user profile page
   - Will display ratings and feedback

---

## Time Breakdown

| Phase | Steps | Time |
|-------|-------|------|
| Get Token | 1.1-1.4 | 1 min |
| Postman Setup | 2.1-2.3 | 2 min |
| Single Test | 3.1-3.3 | 1 min |
| All Endpoints | 4.1-4.3 | 2 min |
| Optional Collection | 5.1-5.3 | 3 min |
| **TOTAL** | | **9 minutes** |

---

## Quick Reference Commands

```bash
# Terminal 1: Start Flask backend
cd backend
python app.py

# Terminal 2: Start Frontend dev server
cd frontend
npm run dev

# Terminal 3: Get token (anytime)
python troubleshoot.py
```

---

## Success Criteria

✅ You know this works when:
1. `python troubleshoot.py` completes with all green checks
2. Postman GET request to `/api/mongodb/transactions` returns 200 OK
3. Response body has `"success": true`
4. You can see transaction data (even if empty list)
5. Token works for multiple different endpoints

---

**Ready to start?** Go to Step 1.1! 🚀
