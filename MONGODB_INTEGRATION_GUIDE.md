# MongoDB Integration Guide - FRNS Frontend

## Overview
Your project already has MongoDB integrated on the backend with activity logging, analytics, notifications, food images, food notes, and route optimization features. This guide shows how to fully leverage these features in your React frontend.

## Current Architecture

### Backend MongoDB Setup ✅
- **MongoDB Service**: `backend/mongodb.py` handles all database operations
- **Collections**:
  - `activity_logs` - User activities (logins, food posts, requests, etc.)
  - `redistribution_analytics` - Food redistribution metrics
  - `feedback` - User feedback
  - `notifications` - Push notifications
  - `food_images` - Food item images
  - `food_notes` - Additional notes for food items
  - `optimized_routes` - Cached route optimization results
  - `geo_cache` - Geolocation data

### Frontend API Integration ✅
- **API Module**: `frontend/src/lib/api.ts` has `mongodb` namespace with methods
- **Components**: MongoDB-specific components in `frontend/src/components/mongodb/`

---

## Implementation Guide

### 1. Setting Up Environment Variables

**Backend (.env)**
```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=frns_db
```

For production (MongoDB Atlas):
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/frns_db?retryWrites=true&w=majority
MONGO_DB=frns_db
```

### 2. Backend Endpoints (Already Implemented)

#### Analytics Endpoints

**GET `/api/analytics/summary`**
```javascript
// Frontend usage
const data = await api.mongodb.getAnalytics();
// Returns: { total_food_saved_kg, total_people_fed, total_carbon_saved, weekly_trend }
```

**POST `/api/analytics/log-redistribution`**
```javascript
await fetch(`${API_BASE}/api/analytics/log-redistribution`, {
  method: 'POST',
  headers: getHeaders(),
  body: JSON.stringify({
    receiver_id: 123,
    food_id: 456,
    quantity_kg: 5,
    food_type: "vegetables"
  })
});
```

**GET `/api/analytics/trends/demand`** (Admin only)
```javascript
// Get demand trends for specific food types
const trends = await fetch(`${API_BASE}/api/analytics/trends/demand?days=7`, {
  headers: getHeaders()
});
```

#### Activity Logging Endpoints

**GET `/logs/activities`**
```javascript
// Frontend usage
const data = await api.mongodb.getActivities(limit);
// Returns: { activities: [...], success: true }
```

Activity types logged:
- `login_success` - User logged in
- `feedback_submitted` - User submitted feedback
- `food_image_uploaded` - Food image was uploaded
- `route_optimized` - Route was optimized
- `food_added` - Food donation added
- `request_created` - Food request created
- `transaction_completed` - Transaction completed
- `profile_updated` - Profile was updated

#### Food Images Endpoints

**GET `/api/food/{foodId}/images`**
```javascript
const images = await api.mongodb.getFoodImages(foodId);
```

**POST `/api/food/{foodId}/images`** (Upload)
```javascript
const formData = new FormData();
formData.append('image', imageFile);
await api.mongodb.uploadFoodImage(foodId, formData);
```

#### Food Notes Endpoints

**GET `/api/notes/food/{foodId}`**
```javascript
const notes = await api.mongodb.getFoodNotes(foodId);
```

**POST `/api/notes/food/{foodId}`**
```javascript
await api.mongodb.addFoodNote(foodId, {
  note_type: "storage_instruction",
  content: "Keep refrigerated",
  metadata: { priority: "high" }
});
```

#### Route Optimization Endpoint

**POST `/api/routes/optimize`**
```javascript
const optimized = await api.mongodb.optimizeRoute({
  pickup_points: [
    [28.7041, 77.1025, 10, "Warehouse A"],
    [28.6139, 77.2090, 15, "Warehouse B"]
  ],
  delivery_points: [
    [28.5244, 77.1855, 8, "Shelter 1"],
    [28.6505, 77.2303, 12, "Shelter 2"]
  ]
});
```

---

## Frontend Component Examples

### 1. Activities Feed Component

**Already exists**: `frontend/src/components/mongodb/ActivitiesFeed.tsx`

Shows recent user activities with icons and timestamps.

**Usage**:
```tsx
import { ActivitiesFeed } from '@/components/mongodb/ActivitiesFeed';

export function Dashboard() {
  return (
    <div>
      <ActivitiesFeed />
    </div>
  );
}
```

### 2. Analytics Dashboard Component

**Already exists**: `frontend/src/components/mongodb/AnalyticsDashboard.tsx`

Displays:
- Total food saved (kg)
- People fed
- Carbon emissions saved
- Weekly trend

**Usage**:
```tsx
import { AnalyticsDashboard } from '@/components/mongodb/AnalyticsDashboard';

export function Dashboard() {
  return (
    <div>
      <AnalyticsDashboard />
    </div>
  );
}
```

### 3. Route Optimizer Component

**Already exists**: `frontend/src/components/mongodb/RouteOptimizer.tsx`

Optimizes delivery routes for volunteers.

### 4. Food Images Component

**Already exists**: `frontend/src/components/food/FoodImages.tsx`

Display and upload food item images.

---

## Adding New MongoDB Features

### Example 1: Feedback History Component

**Create**: `frontend/src/components/mongodb/FeedbackHistory.tsx`

```tsx
import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export const FeedbackHistory: React.FC<{ userId: number }> = ({ userId }) => {
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadFeedbacks = async () => {
      try {
        const data = await api.mongodb.getFeedbackHistory(userId);
        setFeedbacks(data.feedbacks || []);
      } catch (error) {
        console.error('Failed to load feedbacks:', error);
      } finally {
        setLoading(false);
      }
    };

    loadFeedbacks();
  }, [userId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-4">
      {feedbacks.map((feedback) => (
        <div key={feedback._id} className="p-4 border rounded-lg">
          <h4 className="font-semibold">{feedback.type}</h4>
          <p className="text-gray-600">{feedback.content}</p>
          <p className="text-sm text-gray-500 mt-2">
            {new Date(feedback.created_at).toLocaleDateString()}
          </p>
        </div>
      ))}
    </div>
  );
};
```

### Example 2: Real-time Notifications Component

```tsx
import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Fetch notifications
    const loadNotifications = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/notifications/my`, {
          headers: getHeaders()
        });
        const data = await response.json();
        setNotifications(data.notifications || []);
      } catch (error) {
        console.error('Failed to load notifications:', error);
      }
    };

    loadNotifications();

    // Optional: Refresh every 5 seconds
    const interval = setInterval(loadNotifications, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-h-96 overflow-y-auto">
      {notifications.map((notif) => (
        <div 
          key={notif._id}
          className="p-3 border-b hover:bg-gray-50 cursor-pointer"
        >
          <p className="font-medium">{notif.title}</p>
          <p className="text-sm text-gray-600">{notif.message}</p>
          <p className="text-xs text-gray-500 mt-1">
            {new Date(notif.created_at).toLocaleDateString()}
          </p>
        </div>
      ))}
    </div>
  );
};
```

### Example 3: Analytics Trends Chart

```tsx
import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export const DemandTrendsChart: React.FC = () => {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTrends = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/analytics/trends/demand?days=7`, {
          headers: getHeaders()
        });
        const data = await response.json();
        setTrends(data.trends || []);
      } catch (error) {
        console.error('Failed to load trends:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTrends();
  }, []);

  if (loading) return <div>Loading trends...</div>;

  return (
    <div className="space-y-4">
      {trends.map((trend) => (
        <div key={trend.food_type} className="p-4 border rounded">
          <h4 className="font-semibold">{trend.food_type}</h4>
          <p className="text-lg text-blue-600">
            {trend.total_quantity} units requested
          </p>
          <p className="text-sm text-gray-600">
            Avg. Urgency: {trend.avg_urgency.toFixed(1)}/3
          </p>
        </div>
      ))}
    </div>
  );
};
```

---

## Integration Points in Dashboard

### Add to Dashboard.tsx

```tsx
import { ActivitiesFeed } from '@/components/mongodb/ActivitiesFeed';
import { AnalyticsDashboard } from '@/components/mongodb/AnalyticsDashboard';
import { RouteOptimizer } from '@/components/mongodb/RouteOptimizer';

export function Dashboard() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
      {/* Existing content */}
      
      {/* MongoDB Features */}
      <div className="lg:col-span-3">
        <AnalyticsDashboard />
      </div>
      
      <div className="lg:col-span-2">
        <ActivitiesFeed />
      </div>
      
      <div>
        <RouteOptimizer />
      </div>
    </div>
  );
}
```

---

## Best Practices

### 1. Error Handling
```tsx
try {
  const data = await api.mongodb.getAnalytics();
  setAnalytics(data);
} catch (error) {
  console.error('Failed to fetch analytics:', error);
  // Show user-friendly error message
}
```

### 2. Loading States
```tsx
const [loading, setLoading] = useState(true);
useEffect(() => {
  loadData().finally(() => setLoading(false));
}, []);

if (loading) return <Skeleton />;
```

### 3. Real-time Updates
```tsx
// Refresh data periodically
useEffect(() => {
  const interval = setInterval(loadData, 5000); // 5 seconds
  return () => clearInterval(interval);
}, []);
```

### 4. Caching
```tsx
// Store analytics in context or state to avoid repeated fetches
const [analyticsCache, setAnalyticsCache] = useState(null);
const [cacheTime, setCacheTime] = useState(null);

const getAnalytics = async () => {
  const now = Date.now();
  if (analyticsCache && now - cacheTime < 60000) {
    return analyticsCache; // Use cache if < 1 min old
  }
  const data = await api.mongodb.getAnalytics();
  setAnalyticsCache(data);
  setCacheTime(now);
  return data;
};
```

---

## Debugging MongoDB Connection

### Check Backend Connection
```bash
# In backend directory
python
>>> from backend.mongodb import mongo_service
>>> print(mongo_service.connected)
True  # Should print True if connected
```

### View MongoDB Data
```bash
# Using MongoDB CLI
mongosh
> use frns_db
> db.activity_logs.find().limit(5)
> db.redistribution_analytics.findOne()
```

### Network Debugging
In your browser DevTools:
1. Open Network tab
2. Filter for `/api/analytics`, `/api/routes`, `/logs` requests
3. Check response status and data

---

## Next Steps

1. ✅ Verify MongoDB is running locally or connected to MongoDB Atlas
2. ✅ Test each endpoint with Postman/Thunder Client
3. ✅ Integrate components into your main Dashboard
4. ✅ Add error boundaries for MongoDB features
5. ✅ Implement caching for frequently accessed data
6. ✅ Add real-time updates with WebSockets (already set up with socketio in backend)
7. ✅ Create admin analytics views for advanced metrics

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB connection fails | Check `MONGO_URI` in `.env`, ensure MongoDB service is running |
| Empty activities/analytics | Ensure users are performing actions (logins, food posts, etc.) |
| CORS errors | Verify `CORS_ORIGINS` in backend config includes your frontend URL |
| Images not uploading | Check file size limits, ensure `multer` is configured |
| Slow queries | Check indexes in MongoDB, consider pagination for large datasets |

---

## Database Schema Examples

### Activity Log
```javascript
{
  _id: ObjectId("..."),
  user_id: "123",
  activity_type: "login_success",
  details: { method: "password" },
  ip_address: "192.168.1.1",
  created_at: ISODate("2025-01-15T10:30:00Z")
}
```

### Analytics Record
```javascript
{
  _id: ObjectId("..."),
  donor_id: "123",
  receiver_id: "456",
  food_id: "789",
  quantity_kg: 5,
  food_type: "vegetables",
  timestamp: ISODate("2025-01-15T10:30:00Z")
}
```

### Food Image
```javascript
{
  _id: ObjectId("..."),
  food_id: "789",
  image_url: "https://...",
  mime_type: "image/jpeg",
  size_bytes: 102400,
  created_at: ISODate("2025-01-15T10:30:00Z")
}
```

---

## Performance Tips

1. **Pagination**: Use limit/offset for large datasets
```tsx
const getActivities = async (page = 1, pageSize = 20) => {
  const response = await fetch(
    `${API_BASE}/logs/activities?limit=${pageSize}&offset=${(page-1) * pageSize}`,
    { headers: getHeaders() }
  );
  return response.json();
};
```

2. **Aggregation**: Use MongoDB aggregation pipeline for complex queries
3. **Indexing**: Ensure MongoDB indexes are created (done in `mongodb.py`)
4. **Caching**: Cache analytics summary (data doesn't change frequently)

