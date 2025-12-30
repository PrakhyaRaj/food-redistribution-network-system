# Socket.IO Quick Start - Get Real-Time Notifications Working

## 🚀 Start in 3 Steps

### Step 1: Start the Backend
```bash
# From project root directory
cd c:\Users\Prakhya Raj\OneDrive\Desktop\FRNS\food-redistribution-network-system

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start the Flask backend with Socket.IO
python backend/app.py
```

You should see output like:
```
Using database: postgresql://postgres:***@localhost:5432/frns
✅ MongoDB connected successfully!
Using database: ...
 * Running on http://127.0.0.1:5000
 * WARNING: This is a development server. Do not use it in production.
 * Press CTRL+C to quit
```

### Step 2: Start the Frontend
```bash
# Open a NEW terminal
cd c:\Users\Prakhya Raj\OneDrive\Desktop\FRNS\food-redistribution-network-system\frontend

# Start Vite dev server
npm run dev
```

You should see:
```
  VITE v4.x.x  ready in 500 ms
  ➜  Local:   http://localhost:5173/
  ➜  Press q to stop
```

### Step 3: Test Real-Time Notifications
1. Open browser: http://localhost:5173
2. **Login as Receiver**
   - Email: `receiver@example.com`
   - Password: `password123`
3. **Create a Request**
   - Click "Create Request"
   - Select food type: "vegetables"
   - Set quantity: 5
   - Set urgency: "high"
   - Click "Create"
4. **Open Second Browser Tab/Window (or Incognito)**
5. **Login as Donor**
   - Email: `donor@example.com`
   - Password: `password123`
6. **Create a Food Item**
   - Click "Add Food Item"
   - Name: "Fresh Vegetables"
   - Quantity: 10
   - Set expiry date: 3 days from now
   - Click "Add"
7. **Create Transaction**
   - Find the request from step 3
   - Click "Create Transaction" or "Accept"
8. **Watch Magic Happen! ✨**
   - Switch back to receiver's tab
   - You should see a toast notification: "🎉 Match Found!"
   - Real-time update from backend via Socket.IO!

## 🔍 Debug Checklist

### Backend Issues
- [ ] Backend started on port 5000? (`python backend/app.py`)
- [ ] PostgreSQL running? (Check database URI in output)
- [ ] MongoDB running? (Check "MongoDB connected" message)
- [ ] No import errors? (All files should load without errors)

### Frontend Issues
- [ ] Frontend started on port 5173? (`npm run dev`)
- [ ] Can login successfully?
- [ ] Browser DevTools open (F12) to check console logs?

### Connection Issues
- [ ] Check browser console: Should show "✅ Connected to notification server"
- [ ] Check backend logs: Should show "🔌 User 9 connected with SID ..."
- [ ] Try creating transaction - backend should log: "✅ Match notifications emitted"

### Still Having Issues?
1. Check if ports are available:
   ```bash
   netstat -ano | findstr :5000
   netstat -ano | findstr :5173
   ```
2. Clear browser cache and cookies
3. Reload frontend (Ctrl+R)
4. Restart both backend and frontend

## 📊 Test Full Flow Automatically

Run the automated test to verify everything works:

```bash
# From project root
python test_socketio_transactions.py
```

This will:
1. Login as both donor and receiver
2. Create a food item and request
3. Create a transaction
4. Verify transaction is in MongoDB
5. Check notifications endpoint
6. Report overall status

Expected success output:
```
✅ All tests PASSED!
✅ Transaction created - ID: X
✅ Retrieved N transactions from MongoDB
```

## 🎯 What Should Happen

### Creating a Transaction
```
1. Receiver clicks "Create Transaction"
   ↓
2. POST /requests/{id}/matches/{id}/create-transaction sent to backend
   ↓
3. Backend creates SQL transaction + MongoDB record
   ↓
4. Socket.IO emits 'match_found' to user_{receiver_id} and user_{donor_id}
   ↓
5. Frontend receives message in real-time
   ↓
6. Toast notification appears: "🎉 Match Found!"
```

### Behind the Scenes
```
Backend logs show:
🔵 Storing transaction 6 to MongoDB
✅ Transaction 6 stored to MongoDB
✅ Match notifications emitted for request 5 to both parties

Frontend shows:
- 🎉 Match Found!
- Match found! Fresh Vegetables matches your request
- [View Match] button
```

## 🔗 Useful Endpoints

### Create Transaction
```
POST /requests/{request_id}/matches/{food_id}/create-transaction
Headers: Authorization: Bearer {token}
Response: 201 Created
```

### Get Transactions
```
GET /api/mongodb/transactions
Headers: Authorization: Bearer {token}
Response: {transactions: [...], count: N}
```

### Get Notifications
```
GET /api/mongodb/notifications
Headers: Authorization: Bearer {token}
Response: {notifications: [...]}
```

## 💡 Pro Tips

1. **Use Multiple Browsers**
   - Chrome for receiver
   - Firefox for donor
   - Watch notifications in real-time!

2. **Keep Backend Console Visible**
   - See logs as transactions happen
   - Helps with debugging

3. **Use Browser DevTools**
   - Open Console (F12) to see WebSocket traffic
   - Look for "match_found" events
   - Check for connection errors

4. **Test Offline/Online**
   - Disconnect donor tab
   - Create transaction
   - Reconnect donor tab
   - Both should work (thanks to MongoDB persistence)

## 🚨 Common Errors & Fixes

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'backend'` | Run from project root, not backend/ directory |
| `RuntimeError: Either 'SQLALCHEMY_DATABASE_URI' or 'SQLALCHEMY_BINDS' must be set` | Missing config.py or environment variables |
| `Connection refused: [Errno 111]` | PostgreSQL or MongoDB not running |
| `Port 5000 already in use` | `netstat -ano \| findstr :5000` to find what's using it |
| `CORS error in frontend` | Backend CORS is configured, restart if still failing |
| `WebSocket connection failed` | Check backend is running and port 5000 is accessible |

## 📱 Test Notifications

### See in Browser DevTools
```javascript
// Copy/paste in browser console while connected:
socket.emit('test_notification', {message: 'test'})
```

### Manual Postman Test
1. Create transaction via POST endpoint
2. Check GET /api/mongodb/transactions returns it
3. Check frontend received 'match_found' event (check console)

## 🎓 Understanding the Flow

```
┌─────────────────────────────────────────────────┐
│ User creates transaction in browser (React)     │
└─────────────────┬───────────────────────────────┘
                  │
                  ↓ HTTP POST
┌─────────────────────────────────────────────────┐
│ Backend Flask receives POST request             │
│ - Validates user is receiver                    │
│ - Creates SQL transaction                       │
│ - Stores copy in MongoDB                        │
└─────────────────┬───────────────────────────────┘
                  │
                  ↓ Python function call
┌─────────────────────────────────────────────────┐
│ notify_match_found() function                   │
│ - Emits Socket.IO event to donor room           │
│ - Emits Socket.IO event to receiver room        │
└─────────────────┬───────────────────────────────┘
                  │
                  ↓ WebSocket broadcast
┌─────────────────────────────────────────────────┐
│ Browser receives 'match_found' event            │
│ - Toast notification displays                   │
│ - App state updates                             │
│ - UI refreshes                                  │
└─────────────────────────────────────────────────┘
```

## ✅ Verification Checklist

- [ ] Backend started: `python backend/app.py`
- [ ] Frontend started: `npm run dev`
- [ ] Can login as receiver
- [ ] Can login as donor
- [ ] Can create food item
- [ ] Can create request
- [ ] Can create transaction (HTTP 201)
- [ ] See toast notification on receiver side
- [ ] Backend logs show "✅ Match notifications emitted"
- [ ] Transaction appears in GET /api/mongodb/transactions

**If all ✅, Socket.IO real-time notifications are working! 🎉**

## 🆘 Need Help?

1. Check `SOCKETIO_FIX_COMPLETE.md` for full documentation
2. Run `python test_socketio_init.py` to verify initialization
3. Run `python test_socketio_transactions.py` for end-to-end test
4. Check backend logs for error messages
5. Check browser DevTools console for client-side errors

---

**You're all set! Create transactions and watch real-time notifications appear!** 🚀
