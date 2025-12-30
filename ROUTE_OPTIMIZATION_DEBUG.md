# Route Optimization Debug Guide

## Changes Made

### Backend Changes
1. **Added `compute_route_data()` helper function** in `backend/routes/transaction_routes.py`
   - Calls RouteOptimizer with OSRM (or haversine fallback)
   - Returns structured data with "success", "route", and "metrics" keys
   - Added extensive debug logging with emoji prefixes (🗺️, ✅, ❌, ⚠️)

2. **Modified transaction creation** in `backend/routes/transaction_routes.py`
   - Now calls `compute_route_data()` immediately when transaction is created
   - Stores route_data in MongoDB transactions collection
   - Logs every step: donor/receiver fetch, route computation, MongoDB storage

3. **Added sorting to MongoDB API** in `backend/routes/mongodb_routes.py`
   - Transactions now returned newest-first (sorted by created_at/date/txn_id)
   - Ensures fallback always gets the most recent transaction with route_data

### Frontend Changes
1. **Enhanced RouteOptimization.tsx** with detailed console logging
   - Logs every fetch attempt with 🗺️ prefix
   - Shows transaction data, route_data structure, and mapping results
   - Helps identify where the chain breaks

## How to Debug

### Step 1: Restart Backend
```powershell
cd backend
python app.py
```

### Step 2: Create a New Transaction
- Login as a donor
- Add food item
- Login as receiver (different browser/incognito)
- Create request and match with donor's food

### Step 3: Check Backend Console
Look for these log messages:
```
🗺️ [ROUTE] Starting route computation...
🗺️ [ROUTE] Donor: <name>, Receiver: <name>
✅ OSRM API: Distance=X.XXkm, Duration=X.Xmin
✅ Using OSRM distance: X.XXkm
✅ [ROUTE] Using full optimization result
🗺️ [TRANSACTION] Route data computed: True
🗺️ [TRANSACTION] Route details: {...}
✅ [TRANSACTION] Route optimization stored
✅ [TRANSACTION] Transaction stored in MongoDB with route_data
```

### Step 4: Check Frontend Console (Browser DevTools)
Look for these log messages:
```
🗺️ [RouteOptimization] Starting fetch, transactionId: X
🗺️ [RouteOptimization] Response status: 200
🗺️ [RouteOptimization] Response data: {transactions: [...]}
🗺️ [RouteOptimization] Transaction route_data: {...}
✅ [RouteOptimization] Setting route data from transaction
```

## Common Issues & Fixes

### Issue: "No route data found in transaction"
**Cause**: Transaction created before these changes
**Fix**: Create a new transaction after restarting backend

### Issue: "MongoDB not connected"
**Cause**: MongoDB service not running
**Fix**: 
```powershell
# Start MongoDB (if using local installation)
net start MongoDB

# Or check docker containers
docker ps
```

### Issue: "OSRM API timeout"
**Cause**: Internet connectivity or OSRM service down
**Result**: Automatically falls back to haversine distance calculation
**Note**: This is expected behavior, route_data will still be stored

### Issue: "Fallback badge showing"
**Cause**: Current transaction has no route_data
**Check**: 
1. Was transaction created after backend restart?
2. Do both users have valid lat/long coordinates in profiles?
3. Check backend logs for route computation errors

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Create new transaction
- [ ] Backend logs show route computation success
- [ ] MongoDB logs show transaction storage success
- [ ] Frontend shows route optimization card (no "Last completed" badge)
- [ ] Route shows distance, time, and metrics
- [ ] Badge shows "🗺️ Map API" or "📍 Estimated"

## Quick Test Users

Make sure test users have valid coordinates:
- Donor: lat=23.76, long=76.34 (Bhopal area)
- Receiver: lat=23.77, long=76.35 (nearby)

Update in Profile if needed!
