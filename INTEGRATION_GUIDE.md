# 🚀 INTEGRATION GUIDE - Step by Step

## How to Integrate New Features into Your UI

### Step 1: Add MatchedFoods to Request Detail Page

**Location**: `frontend/src/pages/RequestDetail.tsx` (or wherever request detail is)

```typescript
import { MatchedFoods } from '@/components/requests/MatchedFoods';

export function RequestDetail({ requestId }) {
  const [request, setRequest] = useState(null);

  useEffect(() => {
    // Fetch request details
  }, [requestId]);

  return (
    <div className="space-y-6">
      {/* Existing request details */}
      <RequestInfo request={request} />
      
      {/* NEW: Show matched foods */}
      <div className="mt-8 border-t pt-8">
        <h2 className="text-2xl font-bold mb-4">Find Matching Food</h2>
        <MatchedFoods 
          requestId={request.request_id}
          foodType={request.food_type}
          quantity={request.quantity}
        />
      </div>
    </div>
  );
}
```

---

### Step 2: Add TransactionHistory to Dashboard

**Location**: `frontend/src/pages/Dashboard.tsx`

```typescript
import { TransactionHistory } from '@/components/mongodb/TransactionHistory';

export function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Existing dashboard content */}
      <AnalyticsDashboard />
      <NotificationCenter />
      
      {/* NEW: Transaction history */}
      <TransactionHistory />
      
      {/* Rest of dashboard */}
    </div>
  );
}
```

---

### Step 3: Add ProfileFeedback to Profile Page

**Location**: `frontend/src/pages/Profile.tsx`

```typescript
import { ProfileFeedback } from '@/components/profile/ProfileFeedback';
import { TransactionHistory } from '@/components/mongodb/TransactionHistory';

export function Profile() {
  const { userId } = useAuth();

  return (
    <div className="space-y-8">
      {/* Existing profile content */}
      <ProfileHeader userId={userId} />
      
      {/* NEW: Feedback section */}
      <div className="border-t pt-8">
        <h2 className="text-2xl font-bold mb-6">Community Feedback</h2>
        <ProfileFeedback userId={userId} />
      </div>
      
      {/* NEW: Transaction history */}
      <div className="border-t pt-8">
        <h2 className="text-2xl font-bold mb-6">My Transactions</h2>
        <TransactionHistory />
      </div>
    </div>
  );
}
```

---

### Step 4: Verify Notification Handler is in App Root

**Location**: `frontend/src/App.tsx`

```typescript
import NotificationHandler from '@/components/NotificationHandler';

function App() {
  return (
    <div>
      {/* Add notification handler at root level */}
      <NotificationHandler />
      
      {/* Rest of app */}
      <Router>
        <Routes>
          {/* Routes */}
        </Routes>
      </Router>
    </div>
  );
}
```

---

## Backend Verification

### Verify All Routes Are Registered

Run this in Python shell to check:

```python
from backend.app import create_app

app = create_app()

# Check registered routes
with app.app_context():
    routes = []
    for rule in app.url_map.iter_rules():
        if 'request' in rule.rule or 'mongodb' in rule.rule:
            routes.append(f"{rule.methods} {rule.rule}")
    
    for route in sorted(routes):
        print(route)
```

### Expected Output:
```
POST /requests/<request_id>/find-matches
POST /requests/<request_id>/matches/<food_id>/create-transaction
POST /requests/donor/<food_id>/find-requests
GET /api/mongodb/transactions
GET /api/mongodb/transactions/<txn_id>
PUT /api/mongodb/transactions/<txn_id>/update-status
GET /api/mongodb/route-optimizations/<request_id>
GET /api/mongodb/notifications/<user_id>
GET /api/mongodb/feedback/user/<user_id>
GET /api/mongodb/activities/<user_id>
... (other routes)
```

---

## Testing the Integration

### Test Case 1: Receiver Creates Request and Finds Matches

```bash
# 1. Login as receiver
# GET /auth/login with credentials

# 2. Create a request
# POST /requests/add_request
{
  "food_type": "rice",
  "quantity": 5,
  "urgency_level": "medium"
}
# Returns: request_id = 123

# 3. Find matches for the request
# POST /requests/123/find-matches
# Returns: List of matching foods with routes

# 4. View in UI
# Navigate to request detail page
# See MatchedFoods component populate with data
```

### Test Case 2: Accept a Match and Check Transaction

```bash
# 1. From matched foods list, accept a match
# POST /requests/123/matches/456/create-transaction
# Returns: transaction_id = 789

# 2. Check notifications
# Should see toast: "🎉 Match Found!"

# 3. View transaction history
# GET /api/mongodb/transactions
# Should see transaction #789 in list

# 4. Check MongoDB
db.transactions.find({ txn_id: 789 })
# Should return complete transaction record
```

### Test Case 3: Check Profile Feedback

```bash
# 1. Navigate to profile page
# Should see ProfileFeedback component loaded

# 2. If user has feedback:
# - Average rating displayed
# - Feedback list shown
# - Statistics calculated

# 3. Verify backend call:
# GET /api/mongodb/feedback/user/{user_id}
# Returns feedback records
```

---

## Troubleshooting

### Problem: MatchedFoods not showing data

**Solution**:
```python
# 1. Verify backend is running
curl http://127.0.0.1:5000/requests/123/find-matches \
  -H "Authorization: Bearer {token}" \
  -X POST

# 2. Check logs for matching service errors
# Should see: "✅ Finding matches for request..."

# 3. Verify MongoDB connection
# In app.py logs, should see: "✅ MongoDB connected successfully!"
```

### Problem: Notifications not appearing

**Solution**:
```typescript
// 1. Check NotificationHandler mounted
// Open browser console, should see:
// "🔌 WebSocket status: connected"

// 2. Verify socket.io connection
// In browser console:
console.log('Socket connected:', window.socket?.connected);

// 3. Check backend for socket emission
# In backend logs, should see match notifications being emitted
```

### Problem: TransactionHistory empty

**Solution**:
```python
# 1. Verify MongoDB is running
docker ps | grep mongo

# 2. Check if transactions exist
db.transactions.countDocuments()

# 3. Verify user has transactions
db.transactions.find({ 
  "$or": [
    {"donor_id": 1},
    {"receiver_id": 1}
  ]
})
```

---

## Performance Optimization

### Add Pagination to TransactionHistory

```typescript
// Update TransactionHistory.tsx
const [page, setPage] = useState(0);
const [pageSize, setPageSize] = useState(10);

// In API call:
const response = await fetch(
  `${API_BASE}/api/mongodb/transactions?page=${page}&limit=${pageSize}`
);
```

### Implement Route Caching

```python
# In route_optimizer.py
# Routes are already cached in MongoDB
# Cache expires after 24 hours
# Repeated route calculations hit cache first

# To clear cache:
mongo_service.db['optimized_routes'].delete_many({})
```

### Add Request Debouncing for Matches

```typescript
// In MatchedFoods.tsx - debounce refresh
const debouncedFindMatches = useMemo(
  () => debounce(findMatches, 1000),
  []
);
```

---

## Monitoring & Debugging

### Check MongoDB Collections

```bash
# Connect to MongoDB
mongosh

# Switch to database
use frns_db

# Check collections
show collections

# Check transaction data
db.transactions.find().limit(5)

# Check route optimizations
db.route_optimizations.find().limit(5)

# Check match notifications
db.match_notifications.find().limit(5)
```

### Backend Logs to Watch For

```
✅ Matching found X matches
✅ Route optimization completed
✅ Transaction created with ID xxx
✅ Match notification stored
✅ Activity logged for user xxx
```

### Frontend Console

```
[INFO] MatchedFoods: Data loaded
[INFO] TransactionHistory: Fetched N transactions
[INFO] ProfileFeedback: Stats calculated
[INFO] Notifications: Match found! Toast shown
```

---

## Production Checklist

Before deploying to production:

- [ ] All MongoDB collections have proper indexes
- [ ] Error handling covers all edge cases
- [ ] Rate limiting implemented for matching endpoints
- [ ] User authentication verified on all endpoints
- [ ] Frontend components have loading states
- [ ] Toast notifications auto-dismiss properly
- [ ] Database backups configured
- [ ] Socket.io properly configured for production
- [ ] Environment variables set correctly
- [ ] CORS settings for production domain
- [ ] HTTPS enabled
- [ ] Monitoring and logging configured

---

## Rollback Plan

If issues occur:

```bash
# 1. Revert database changes (no schema changes made)
# All data in PostgreSQL is compatible with old version

# 2. Clear MongoDB collections if corrupted
mongo
use frns_db
db.transactions.deleteMany({})
db.route_optimizations.deleteMany({})
db.match_notifications.deleteMany({})

# 3. Revert code changes if needed
git revert <commit-hash>

# 4. Restart services
pkill -f "python app.py"
python app.py
```

---

## Success Indicators

✅ You'll know everything is working when:

1. **Matching Works**
   - Create request → Matches appear with distances
   - Accept match → Transaction created

2. **Notifications Work**
   - Toast appears when match found
   - Both parties notified via socket.io

3. **MongoDB Works**
   - Transaction stored in db.transactions
   - Route data saved with transaction
   - Can query transactions by user

4. **Frontend Works**
   - MatchedFoods displays data
   - TransactionHistory shows transactions
   - ProfileFeedback shows ratings

5. **Performance Good**
   - Matches found in < 2 seconds
   - Route optimization in < 1 second
   - Components load instantly with data

---

## Support

For issues or questions:

1. Check IMPLEMENTATION_GUIDE_COMPLETE.md
2. Review API endpoint responses with curl
3. Check MongoDB data directly
4. Review backend logs
5. Check browser console for errors

---

**Integration Status**: ✅ READY TO DEPLOY

All components created and documented. Follow steps above to integrate into your UI.
