# MongoDB Integration - Quick Reference Card

## Import Components
```tsx
import {
  ActivitiesFeed,
  AnalyticsDashboard,
  NotificationCenter,
  FeedbackInsights,
  FoodNotesManager,
  FoodImages,
  RouteOptimizer,
} from '@/components/mongodb';
```

## Use in Components
```tsx
// Activities - shows user actions
<ActivitiesFeed />

// Analytics - shows food saved, people fed, carbon saved
<AnalyticsDashboard />

// Notifications - shows real-time notifications with count
<NotificationCenter />

// Feedback - shows user feedback stats and history
<FeedbackInsights />

// Notes - add/view notes for food items
<FoodNotesManager foodId={123} />

// Images - view/upload food images
<FoodImages foodId={123} />

// Routes - optimize delivery routes
<RouteOptimizer />
```

## API Calls
```typescript
import { api } from '@/lib/api';

// Get activities
await api.mongodb.getActivities(limit: number);

// Get analytics
await api.mongodb.getAnalytics();

// Optimize route
await api.mongodb.optimizeRoute({
  pickup_points: [[lat, lon, qty, name], ...],
  delivery_points: [[lat, lon, qty, name], ...]
});

// Food images
await api.mongodb.getFoodImages(foodId);
await api.mongodb.uploadFoodImage(foodId, formData);

// Food notes
await api.mongodb.getFoodNotes(foodId);
await api.mongodb.addFoodNote(foodId, {
  note_type: 'storage|recipe|warning|other',
  content: 'text',
  metadata: { priority: 'high|medium|low' }
});

// Feedback history
await api.mongodb.getFeedbackHistory(userId);
```

## Custom Hooks (Level 2)
```typescript
// Create file: frontend/src/hooks/useMongoDB.ts
import { useAnalytics, useActivities, useFoodNotes } from '@/hooks/useMongoDB';

// Auto-refresh analytics every 60 seconds
const { data: analytics, loading, error } = useAnalytics({
  refreshInterval: 60000,
  cacheTime: 300000
});

// Get activities with manual refresh
const { data: activities, refetch } = useActivities(10, {
  autoLoad: true
});

// Food notes with add capability
const { notes, addNote, loading } = useFoodNotes(foodId);
```

## Real-time Updates (Level 3)
```typescript
// Create file: frontend/src/contexts/RealtimeContext.tsx
import { useRealtime } from '@/contexts/RealtimeContext';

const { socket, connected, newActivity, newNotification } = useRealtime();

// Then wrap app with RealtimeProvider in App.tsx
<RealtimeProvider>
  <App />
</RealtimeProvider>
```

## MongoDB Collections
| Collection | Purpose | Fields |
|-----------|---------|--------|
| activity_logs | User actions | user_id, activity_type, details, created_at |
| redistribution_analytics | Food metrics | donor_id, receiver_id, quantity_kg, timestamp |
| feedback | User feedback | user_id, rating, content, feedback_type |
| notifications | Push notifs | user_id, title, message, type, read |
| food_images | Food pictures | food_id, image_url, mime_type |
| food_notes | Food notes | food_id, note_type, content, tags |
| optimized_routes | Route cache | waypoints, distance_km, duration_minutes |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No activities showing | Ensure users are logging in/creating posts |
| API 404 errors | Check backend routes in `/api/` prefix |
| CORS errors | Update CORS origins in backend/app.py |
| JWT token invalid | Re-login to get new token |
| MongoDB connection failed | Check .env MONGO_URI and mongod service |
| Components not found | Verify imports from '@/components/mongodb' |

## Environment Setup
```bash
# 1. Start MongoDB
mongosh  # or mongod service on Windows

# 2. Configure backend/.env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=frns_db

# 3. Start backend
cd backend
python app.py  # Port 5000

# 4. Start frontend
cd frontend
npm run dev  # Port 5173
```

## Quick Dashboard Integration
```tsx
import {
  ActivitiesFeed,
  AnalyticsDashboard,
  NotificationCenter,
  FeedbackInsights,
} from '@/components/mongodb';

export function Dashboard() {
  return (
    <div className="grid grid-cols-3 gap-6 p-6">
      <div className="col-span-2"><AnalyticsDashboard /></div>
      <NotificationCenter />
      <div className="col-span-2"><ActivitiesFeed /></div>
      <FeedbackInsights />
    </div>
  );
}
```

## Performance Tips
1. **Cache analytics** - only refresh every 5 minutes
2. **Paginate lists** - show 20 items per page
3. **Use hooks** - share logic with custom hooks
4. **WebSocket** - for real-time notifications
5. **Debounce** - search/filter operations

## Database Queries
```javascript
// View in MongoDB Compass or mongosh

// Get user's activities
db.activity_logs.find({ user_id: "123" }).limit(10)

// Get analytics summary
db.redistribution_analytics.find()

// Get user's notifications
db.notifications.find({ user_id: "123" })

// Get food notes
db.food_notes.find({ food_id: "456" })

// Get food images
db.food_images.find({ food_id: "456" })
```

## File Locations
```
frontend/src/
├── components/mongodb/          ✅ All components
│   ├── ActivitiesFeed.tsx
│   ├── AnalyticsDashboard.tsx
│   ├── NotificationCenter.tsx   ✅ NEW
│   ├── FeedbackInsights.tsx     ✅ NEW
│   ├── FoodNotesManager.tsx     ✅ NEW
│   └── index.ts
├── lib/
│   └── api.ts                   ✅ API client with mongodb methods
└── hooks/
    └── useMongoDB.ts            ✅ Create for Level 2

backend/
├── mongodb.py                   ✅ MongoDB service
├── routes/
│   ├── analytics_routes.py
│   ├── logs_routes.py
│   └── ...                      ✅ All endpoints exposed
└── .env                         ✅ Configure MONGO_URI
```

## Common Endpoints
```
GET  /api/analytics/summary
POST /api/analytics/log-redistribution
GET  /api/analytics/trends/demand

GET  /logs/activities

GET  /api/notifications/my
PUT  /api/notifications/{id}/read
DELETE /api/notifications/{id}

GET  /api/food/{id}/images
POST /api/food/{id}/images

GET  /api/notes/food/{id}
POST /api/notes/food/{id}

POST /api/routes/optimize

GET  /api/feedback/user/{id}
```

## Three Implementation Levels

### Level 1: Quick (5 min) ⚡
- Import components
- Add to Dashboard
- Done!

### Level 2: Better (1-2 hours) 🚀
- Create custom hooks for data fetching
- Add caching & auto-refresh
- Share state with context

### Level 3: Advanced (3-5 hours) 🔥
- Add real-time WebSocket updates
- Create admin analytics dashboard
- Implement pagination & optimization

---

**Last Updated**: January 2025  
**Components**: 7 available  
**API Endpoints**: 15+ available  
**Documentation**: Complete with 4 guides  

**Ready to integrate?** Start with Level 1 - takes 5 minutes!

