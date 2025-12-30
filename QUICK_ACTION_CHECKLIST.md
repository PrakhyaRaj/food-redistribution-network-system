# 🎯 Quick Action Checklist

## START HERE ⬇️

### ✅ Phase 1: Generate Token (30 seconds)
```
[ ] Open PowerShell
[ ] Navigate to project: cd "c:\Users\Prakhya Raj\OneDrive\Desktop\FRNS\food-redistribution-network-system"
[ ] Run: python troubleshoot.py
[ ] Wait for output with green checkmarks
[ ] Copy the token (long string starting with "eyJh")
```

**Save this token for next step!**

---

### ✅ Phase 2: Add to Postman (1 minute)
```
[ ] Open Postman
[ ] Click "Authorization" tab
[ ] Select "Bearer Token" from dropdown
[ ] Paste your token in the Token field
[ ] Do NOT modify anything else
```

**Visual:**
```
Authorization Tab
├─ Type: Bearer Token ▼
└─ Token: [PASTE_HERE]
```

---

### ✅ Phase 3: Test Endpoint (30 seconds)
```
[ ] Create new request in Postman
[ ] Set method: GET
[ ] Enter URL: http://localhost:5000/api/mongodb/transactions
[ ] Click Send
[ ] Check response status: Should be 200 OK ✅
[ ] Check response has: "success": true ✅
```

**If you see 200 OK with success: true → YOU'RE DONE!** 🎉

---

## If Something Goes Wrong

### ❌ Still Getting 403?
```
[ ] Check token is in Authorization tab (NOT Headers tab)
[ ] Check dropdown says "Bearer Token"
[ ] Check full token is pasted (it's very long)
[ ] Flask server running? (python app.py in backend terminal)
[ ] Run troubleshoot.py again for fresh token
```

### ❌ Getting "Token expired"?
```
[ ] Run: python troubleshoot.py
[ ] Copy new token
[ ] Update in Postman
```

### ❌ Getting "MongoDB not available"?
```
[ ] This is OK - API still works
[ ] You can ignore this for now
```

---

## Next Steps After Success

1. **Test All Endpoints:**
   - GET /api/mongodb/test-auth
   - GET /api/mongodb/status
   - GET /api/mongodb/feedback/user/13
   - GET /api/mongodb/activities/13

2. **Optional: Import Postman Collection**
   - File → Import
   - Select: FRNS_API_Postman_Collection.json
   - All endpoints pre-configured

3. **Integrate with Frontend**
   - Add MatchedFoods component
   - Add TransactionHistory component
   - Add ProfileFeedback component

---

## Reference: Files You Need

| File | Purpose | When |
|------|---------|------|
| `troubleshoot.py` | Generate token | Step 1 |
| `2MIN_QUICKSTART.md` | Quick overview | Anytime |
| `STEP_BY_STEP_GUIDE.md` | Detailed steps | This checklist |
| `FRNS_API_Postman_Collection.json` | Postman import | Optional |

---

## Estimated Times

| Step | Time |
|------|------|
| Generate token | 30 sec |
| Add to Postman | 1 min |
| First test | 30 sec |
| Test all endpoints | 2 min |
| **TOTAL** | **4 minutes** |

---

## Success = You See This

```
Status: 200 OK

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

---

## One-Liner Summary

**Generate token → Copy → Paste in Postman → Send → 200 OK ✅**

---

**Questions?** Read `STEP_BY_STEP_GUIDE.md` for details

**Ready?** Start with Phase 1 above! 🚀
