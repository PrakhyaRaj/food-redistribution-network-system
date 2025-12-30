# ⚡ 2-Minute Quick Start

## 🎯 Your 403 Error - SOLVED

### What was wrong?
Missing JWT token in Authorization header

### What's the fix?
Use the valid token from the script

---

## 🚀 DO THIS NOW (Copy & Paste)

### In PowerShell:
```powershell
cd "c:\Users\Prakhya Raj\OneDrive\Desktop\FRNS\food-redistribution-network-system"
python troubleshoot.py
```

### See output like this:
```
✅ User registered successfully!

📋 Token (save this):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MT...
```

### Copy entire token ↑

---

## In Postman:

### 1. Select any request
### 2. Click "Authorization" tab
### 3. Choose "Bearer Token" from dropdown
### 4. Paste token in box
### 5. Click "Send"

### Expected: **200 OK** ✅

---

## That's it! 🎉

You now have:
- ✅ Valid JWT token
- ✅ Working authentication
- ✅ Access to all MongoDB endpoints
- ✅ Can test transactions, feedback, activities

---

## Optional: Import Collection

Want Postman templates ready to go?

1. Download: `FRNS_API_Postman_Collection.json`
2. Postman: File → Import
3. Select the JSON file
4. Run "Register User" request
5. Token auto-saved! ✨

---

## 🔗 Token Info

**Expires in**: 30 minutes  
**Need new one?** Run script again  
**Can't find it?** Check `FIX_403_UNAUTHORIZED.md`

---

## ✅ Working Now?

Test this URL in Postman:
```
GET http://localhost:5000/api/mongodb/transactions
```

With Authorization header:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response should be:
```json
{
  "success": true,
  "transactions": [],
  "stats": {...}
}
```

If yes → **You're done!** 🚀  
If no → Check `POSTMAN_AUTH_GUIDE.md`

---

Done! Enjoy testing! 🎊
