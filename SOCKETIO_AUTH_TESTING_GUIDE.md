# 🧪 Socket.IO Authentication Fix - Testing Guide

## Pre-Test Checklist

- [ ] Backend is running (`python app.py`)
- [ ] Frontend is running (`npm run dev`)
- [ ] Both are on `http://127.0.0.1:5000` and `http://localhost:5173` respectively
- [ ] You have a valid user account

## Test Case 1: Notification Handler Connection ✅

### What This Tests
- Socket.IO connection establishment
- JWT token validation
- Connection status message

### Steps:
1. **Clear browser console** (Ctrl+Shift+K or Cmd+Option+K)
2. **Log in** to the application
3. **Open browser console** and look for:
   ```
   🔌 Attempting to connect to WebSocket...
   🔑 Token found, attempting connection with: Bearer token
   ✅ Connected to notification server
   Real-time notifications enabled
   ```
4. **In backend terminal**, look for:
   ```
   🔑 Token found in query string
   ✅ Token decoded successfully, user_id: 5
   ✅ User 5 connected with SID ..., joined room: user_5
   ```

**✅ Pass Criteria**: No "Authentication failed" errors, see "connected" messages

---

## Test Case 2: Dashboard Auto-Refresh ✅

### What This Tests
- Socket.IO connections on ReceiverDashboard and DonorDashboard
- Real-time data refresh after match acceptance
- Stats update automatically

### Setup:
Create 2 accounts:
- Account A (Receiver)
- Account B (Donor)

### Steps:

**Step 1: Receiver Creates Request**
1. Log in as Account A (Receiver)
2. Go to Dashboard → Receiver Mode
3. Create Request:
   - Food type: "Rice"
   - Quantity: 5 kg
   - Urgency: High
   - Deadline: Tomorrow
4. Note: "Total Requests" = 1

**Step 2: Donor Creates Food**
1. **Open another browser window** or **private window**
2. Log in as Account B (Donor)
3. Go to Dashboard → Donor Mode
4. Add Food:
   - Food name: "Rice" (must match!)
   - Quantity: 10 kg
   - Expiry: 3 days from now
5. Note: "Active Donations" = 1

**Step 3: Find and Accept Match**
1. **Switch back to Account A** (Receiver)
2. Go to Dashboard → My Requests
3. Click on the "Rice" request card
4. Wait for RequestDetail page to load (should show "Loading..." then display)
5. Click "Find Matching Food" or "Refresh"
6. Should see Account B's food in the list
7. Click "Accept Match"
8. You should see:
   ```
   ✅ Match accepted
   🎉 New transaction created!
   ```

**Step 4: Verify Auto-Refresh on ReceiverDashboard**
1. Go back to Dashboard
2. Check stats:
   - [ ] "Active Requests" decreased (1 → 0)
   - [ ] "Fulfilled" increased (0 → 1)
3. If not automatic, reload page:
   - Wait 1-2 seconds (auto-refresh should happen)
   - If not, you'll see stats update on reload

**Step 5: Verify Auto-Refresh on DonorDashboard**
1. **Switch to Account B** (Donor window)
2. Check Dashboard stats:
   - [ ] "Active Donations" decreased (1 → 0)
   - [ ] Food item status changed to "reserved"
3. If not automatic, reload page

**✅ Pass Criteria**: 
- Stats update (either auto or after reload)
- No console errors
- Transaction appears in Transactions page

---

## Test Case 3: Transactions Page Auto-Refresh ✅

### What This Tests
- Socket.IO connection on Transactions page
- Auto-refresh when new transaction is created
- Transaction details display correctly

### Steps:

**From Test Case 2**, after accepting match:

1. Click "Transactions" link
2. Page should load
3. You should see a new transaction:
   ```
   Transaction #1
   Food Item: Rice
   Status: initiated
   Party: Recipient: #6 (or similar)
   Created: [timestamp]
   ```

4. **Open backend console** and verify:
   ```
   📊 Transactions page connected to Socket.IO
   📊 New transaction detected, refreshing...
   ```

5. You should see:
   ```
   New transaction created!
   Refreshing your transaction list...
   ```

**✅ Pass Criteria**:
- Transaction appears immediately after match
- No authentication errors
- Transaction details are correct

---

## Test Case 4: Notifications (Dual User) ✅

### What This Tests
- Notifications broadcast to both parties
- Socket.IO room targeting (user_5, user_6, etc.)
- Real-time notifications

### Setup:
Keep both browser windows open (Account A and Account B)

### Steps:

**From Test Case 2** (when accepting match):

1. **Account A** (Receiver) clicks "Accept Match"
2. **Immediately check both browser windows**:
   - Account A should see toast: "Match accepted"
   - Account A should see toast: "New transaction created"
3. **In backend console**, you should see:
   ```
   socketio.emit('match_found', {...}, room=f"user_6")  # Receiver
   socketio.emit('match_found', {...}, room=f"user_5")  # Donor
   ```

4. **In Account B** (Donor) browser console, you might see:
   ```
   Match notification received: {...}
   ```
   (If DonorDashboard's Socket.IO is listening)

**✅ Pass Criteria**:
- At least receiver gets notification
- No "Authentication failed" errors
- Transaction appears in transactions page

---

## Test Case 5: Connection Recovery ✅

### What This Tests
- Socket.IO reconnection after disconnect
- Continued functionality after network issue

### Steps:

1. **Open Console** in any page
2. **Simulate network issue**:
   ```javascript
   // Paste in browser console
   if (window.__socketInstance) {
     window.__socketInstance.disconnect();
   }
   ```
3. After 1-2 seconds, you should see:
   ```
   🔌 Attempting to reconnect...
   ✅ Connected to notification server
   ```

4. Test a match acceptance again
5. Should work as before

**✅ Pass Criteria**:
- Auto-reconnects within 5 attempts
- All features work after reconnection

---

## Test Case 6: Multiple Concurrent Matches ✅

### What This Tests
- Multiple matches don't break notifications
- Queue handling

### Setup:
3 accounts total

### Steps:

1. Create 3 requests (Account A)
2. Create 3 food items (Account B)
3. Accept all 3 matches rapidly
4. Verify:
   - All 3 transactions appear
   - Dashboard stats correct
   - No duplicate notifications

**✅ Pass Criteria**:
- All 3 transactions show
- No "race conditions"
- Stats accurate

---

## Debugging Common Issues

### Issue: "Notification connection failed: Authentication required"

**Check:**
1. Backend logs show:
   ```
   🔑 Token found in query string
   ✅ Token decoded successfully
   ```
   If you see: `❌ Token validation failed`, the JWT is invalid

2. Frontend logs show token is being sent:
   ```
   🔑 Token found, attempting connection with: Bearer token
   ```

**Fix:**
- Ensure token is valid (not expired)
- Check JWT_SECRET in backend config
- Restart backend

---

### Issue: Dashboard doesn't update after match

**Check:**
1. Backend logs show user connected to socket room:
   ```
   ✅ User 5 connected with SID ..., joined room: user_5
   ```

2. Frontend logs show match_found event received:
   ```
   📦 Match found, refreshing food list...
   ```

3. Network tab shows Socket.IO events being sent

**Fix:**
- Check if socket is connected (browser console)
- Reload page to test if data is actually updated
- Check browser network tab for Socket.IO errors

---

### Issue: Transaction doesn't appear immediately

**Check:**
1. Manually refresh page - does transaction appear? (If yes, it's a Socket.IO issue)
2. Check console for JavaScript errors
3. Check if socket connection is stable

**Fix:**
- Click "Refresh" button on Transactions page manually
- Check Socket.IO logs on backend
- Verify transaction was actually created (check database)

---

## Success Checklist

After all tests:

- [ ] No "Authentication failed" errors
- [ ] Dashboard updates after match (auto or manual refresh)
- [ ] Transactions page shows new transactions
- [ ] Both parties can see notifications (at least receiver)
- [ ] Stats update correctly
- [ ] No console errors

---

## Performance Notes

| Metric | Expected |
|--------|----------|
| Connection time | 100-200ms |
| Dashboard refresh | 1-2 seconds |
| Transaction refresh | 1-2 seconds |
| Notification toast | < 500ms |

---

## Next Steps If Tests Fail

1. **Check backend logs** for error messages
2. **Check browser console** for JavaScript errors
3. **Check Network tab** for failed requests
4. **Verify token is valid** (not expired)
5. **Restart both frontend and backend**
6. **Clear browser cache** (Ctrl+Shift+Delete)

---

**Ready to test! 🚀**

