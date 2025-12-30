# MongoDB Integration Quick Start

## Prerequisites
- MongoDB running locally or MongoDB Atlas account
- Backend Flask server configured
- Frontend React app with Node.js

---

## Setup Steps

### Step 1: Install MongoDB

**Local Installation (Windows):**
```bash
# Download from https://www.mongodb.com/try/download/community
# Run installer and follow prompts
# MongoDB will run as a Windows service on port 27017

# Verify installation
mongosh
> db.adminCommand('ping')
# Should return: { ok: 1 }
```

**Using MongoDB Atlas (Cloud):**
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/frns_db`

### Step 2: Configure Backend

**File: `backend/.env`**
```env
# Local MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=frns_db

# OR for MongoDB Atlas
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/frns_db?retryWrites=true&w=majority
MONGO_DB=frns_db
```

### Step 3: Verify Backend Connection

```bash
cd backend
python
>>> from backend.mongodb import mongo_service
>>> mongo_service.init_app(None)
>>> print("Connected:", mongo_service.connected)
# Should print: Connected: True
```

### Step 4: Test Backend Endpoints

```bash
# Using PowerShell or any HTTP client (Postman, Thunder Client, etc.)

# Get Analytics
$headers = @{
    "Authorization" = "Bearer YOUR_JWT_TOKEN"
    "Content-Type" = "application/json"
}
Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/analytics/summary" -Headers $headers

# Get Activities
Invoke-WebRequest -Uri "http://127.0.0.1:5000/logs/activities?limit=5" -Headers $headers
```

### Step 5: Integrate Components in Frontend

**Update `frontend/src/pages/Dashboard.tsx`:**

```tsx
import React from 'react';
import {
  ActivitiesFeed,
  AnalyticsDashboard,
  NotificationCenter,
  FeedbackInsights,
} from '@/components/mongodb';

export function Dashboard() {
  return (
    <div className="space-y-6 p-6">
      {/* Title */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-600">Welcome to Food Redistribution Network</p>
      </div>

      {/* MongoDB Features Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Analytics */}
        <div className="lg:col-span-2">
          <AnalyticsDashboard />
        </div>

        {/* Notifications */}
        <div>
          <NotificationCenter />
        </div>

        {/* Activities Feed */}
        <div className="lg:col-span-2">
          <ActivitiesFeed />
        </div>

        {/* Feedback Insights */}
        <div>
          <FeedbackInsights />
        </div>
      </div>
    </div>
  );
}
```

### Step 6: Use MongoDB Components in Food Pages

**Update `frontend/src/pages/MyFoods.tsx`:**

```tsx
import { FoodNotesManager } from '@/components/mongodb';
import { FoodImages } from '@/components/mongodb';

export function MyFoods() {
  const [selectedFoodId, setSelectedFoodId] = React.useState<number | null>(null);

  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Food List */}
      <div className="col-span-2">
        {/* Your existing food list */}
      </div>

      {/* MongoDB Features for Selected Food */}
      {selectedFoodId && (
        <div className="space-y-6">
          <FoodImages foodId={selectedFoodId} />
          <FoodNotesManager foodId={selectedFoodId} />
        </div>
      )}
    </div>
  );
}
```

---

## Available Components

### 1. AnalyticsDashboard
**Shows:** Total food saved, people fed, carbon emissions, weekly trends

```tsx
import { AnalyticsDashboard } from '@/components/mongodb';

<AnalyticsDashboard />
```

### 2. ActivitiesFeed
**Shows:** Recent user activities with timestamps and icons

```tsx
import { ActivitiesFeed } from '@/components/mongodb';

<ActivitiesFeed />
```

### 3. NotificationCenter (NEW)
**Shows:** User notifications, unread count, with mark as read/delete

```tsx
import { NotificationCenter } from '@/components/mongodb';

<NotificationCenter />
```

### 4. FeedbackInsights (NEW)
**Shows:** Feedback statistics, ratings, feedback breakdown

```tsx
import { FeedbackInsights } from '@/components/mongodb';

<FeedbackInsights />
```

### 5. FoodNotesManager (NEW)
**Shows:** Notes for food items with priority levels and tags

```tsx
import { FoodNotesManager } from '@/components/mongodb';

<FoodNotesManager foodId={123} />
```

### 6. FoodImages
**Shows:** Images for food items with upload capability

```tsx
import { FoodImages } from '@/components/mongodb';

<FoodImages foodId={123} />
```

### 7. RouteOptimizer
**Shows:** Route optimization for deliveries

```tsx
import { RouteOptimizer } from '@/components/mongodb';

<RouteOptimizer />
```

---

## API Reference

### Analytics
- `GET /api/analytics/summary` - Get analytics summary
- `POST /api/analytics/log-redistribution` - Log a redistribution event
- `GET /api/analytics/trends/demand` - Get demand trends (admin)

### Activities
- `GET /logs/activities?limit=5` - Get recent activities

### Notifications
- `GET /api/notifications/my` - Get user notifications
- `PUT /api/notifications/{id}/read` - Mark as read
- `DELETE /api/notifications/{id}` - Delete notification

### Food Images
- `GET /api/food/{foodId}/images` - Get food images
- `POST /api/food/{foodId}/images` - Upload food image

### Food Notes
- `GET /api/notes/food/{foodId}` - Get food notes
- `POST /api/notes/food/{foodId}` - Add food note

### Feedback
- `GET /api/feedback/user/{userId}` - Get user feedback
- `POST /api/feedback` - Submit feedback

### Route Optimization
- `POST /api/routes/optimize` - Optimize delivery route

---

## Database Connection Troubleshooting

### Issue: MongoDB Connection Fails
```bash
# Check if MongoDB is running
mongosh

# If not running, start it
# Windows: MongoDB should auto-start as service
# Linux: sudo systemctl start mongod
# macOS: brew services start mongodb-community

# Check connection string in backend/.env
# Local: mongodb://localhost:27017/
# Atlas: mongodb+srv://user:pass@cluster.mongodb.net/db
```

### Issue: CORS Errors
```python
# backend/app.py - Ensure CORS includes your frontend URL
CORS(
    app,
    origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
        "http://127.0.0.1:5173",
    ],
    supports_credentials=True,
    allow_headers=["*"],
    methods=["*"],
)
```

### Issue: JWT Token Invalid
```javascript
// frontend/src/lib/api.ts
const getHeaders = () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    console.warn('No access token found. User may need to login.');
  }
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};
```

---

## Testing in Development

### Frontend Development Server
```bash
cd frontend
npm run dev
# Opens at http://localhost:5173
```

### Backend Development Server
```bash
cd backend
python app.py
# Runs at http://127.0.0.1:5000
```

### Database Browser (MongoDB Compass)
```bash
# Download from https://www.mongodb.com/try/download/compass
# Connect to mongodb://localhost:27017/
# Browse collections in frns_db
```

---

## Performance Tips

1. **Enable indexes** (already done in backend):
   - Ensure MongoDB indexes are created for faster queries
   - Check: `db.activity_logs.getIndexes()`

2. **Cache analytics** (implement in frontend):
   ```tsx
   const [cacheTime, setCacheTime] = useState(0);
   const [cachedAnalytics, setCachedAnalytics] = useState(null);

   const getAnalytics = async () => {
     const now = Date.now();
     if (cachedAnalytics && now - cacheTime < 300000) { // 5 min cache
       return cachedAnalytics;
     }
     const data = await api.mongodb.getAnalytics();
     setCachedAnalytics(data);
     setCacheTime(now);
     return data;
   };
   ```

3. **Pagination** (for large datasets):
   ```typescript
   const getActivities = async (page: number = 1) => {
     const limit = 20;
     const offset = (page - 1) * limit;
     return fetch(`${API_BASE}/logs/activities?limit=${limit}&offset=${offset}`);
   };
   ```

4. **Real-time updates** (using WebSockets):
   ```tsx
   useEffect(() => {
     const interval = setInterval(loadActivities, 10000); // Refresh every 10s
     return () => clearInterval(interval);
   }, []);
   ```

---

## Next Steps

1. ✅ Start MongoDB service
2. ✅ Configure `.env` with MongoDB URI
3. ✅ Test backend endpoints with Postman
4. ✅ Add components to Dashboard
5. ✅ Test with actual user data
6. ✅ Deploy MongoDB (Atlas) for production
7. ✅ Set up monitoring and alerts

---

## Documentation Links

- MongoDB Manual: https://docs.mongodb.com/manual/
- MongoDB Atlas: https://docs.atlas.mongodb.com/
- PyMongo: https://pymongo.readthedocs.io/
- Flask-PyMongo: https://flask-pymongo.readthedocs.io/

