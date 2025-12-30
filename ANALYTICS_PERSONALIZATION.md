# Analytics Personalization & Login Page Enhancement

## Changes Made

### 1. Backend - User-Specific Analytics Support

#### File: `backend/routes/analytics_routes.py`
- **Added**: `/api/analytics/global-summary` (public endpoint, no auth required)
  - Returns global analytics for the login page
  - Accessible to everyone
  
- **Modified**: `/api/analytics/summary` 
  - Now supports `user_specific=true` query parameter
  - When `user_specific=true`: Returns analytics for that user only (items they donated/received)
  - When `user_specific=false` or not specified: Returns global analytics (for backward compatibility)

#### File: `backend/mongodb.py`
- **Added**: `get_user_analytics_summary(user_id, days=30)` method
  - Calculates user-specific metrics:
    - `total_food_saved_kg`: Total food quantity for items user donated or received
    - `total_people_fed`: People impacted by user's donations/receptions
    - `total_trees_planted`: Calculated as `carbon_saved / 20` (1 tree per 20 kg CO₂)
    - `total_redistributions`: Count of user's transactions
    - `avg_quantity_per_redistribution`: Average quantity per transaction
  - Filters analytics by: `$or: [{"donor_id": user_id}, {"receiver_id": user_id}]`

### 2. Frontend - API Client Update

#### File: `frontend/src/lib/api.ts`
- **Added**: `getUserAnalytics()` method
  - Calls `/api/analytics/summary?user_specific=true`
  - Returns user-specific analytics for dashboards
  
- **Added**: `getGlobalAnalytics()` method
  - Calls `/api/analytics/global-summary`
  - Public endpoint, no authentication required
  - Used on login page

- **Kept**: `getAnalytics()` method for backward compatibility

### 3. Frontend - Dashboard Component Updates

#### File: `frontend/src/components/mongodb/AnalyticsDashboard.tsx`
- **Modified**: `loadAnalytics()` function
  - Changed from `api.mongodb.getAnalytics()` to `api.mongodb.getUserAnalytics()`
  - Now displays user-specific analytics instead of global
  
- **Updated**: Display labels and metrics
  - Changed title and description to emphasize "Your Impact"
  - Displays trees planted (instead of raw carbon saved) as primary metric
  - Shows: "Trees Planted" based on CO₂ saved (1 tree per 20 kg CO₂)

### 4. Frontend - Login Page Enhancement

#### File: `frontend/src/pages/Login.tsx`
- **New Layout**: Two-column responsive layout
  - Left side (desktop only): Global analytics showcase
  - Right side: Login form
  
- **Added**: Global Analytics Display Section
  - Shows global impact statistics that inspire users to join
  - Three stat cards with icons:
    - 🍲 **Food Saved**: Total kg/tons
    - 👥 **People Fed**: Total people impacted
    - 🌱 **Trees Planted (equiv.)**: Calculated from global CO₂ saved
  
- **Loading State**: Spinner while fetching analytics
- **Fallback**: Graceful message if analytics unavailable
- **Mobile Responsive**: Analytics hidden on mobile, form fills screen
- **Non-Intrusive**: Placeholder doesn't look odd, integrates naturally with page

## Data Flow

### User Dashboard Analytics
```
User opens dashboard
    ↓
DashboardComponent mounts
    ↓
Calls getUserAnalytics()
    ↓
API: GET /api/analytics/summary?user_specific=true
    ↓
Backend gets JWT token, extracts user_id
    ↓
MongoDB: get_user_analytics_summary(user_id)
    ↓
Aggregation filters by donor_id OR receiver_id = user_id
    ↓
Returns user's personal impact metrics
    ↓
Frontend displays: YOUR food saved, YOUR people fed, YOUR trees
```

### Login Page Global Analytics
```
Login page loads
    ↓
useEffect triggers
    ↓
Calls getGlobalAnalytics() [NO AUTH REQUIRED]
    ↓
API: GET /api/analytics/global-summary
    ↓
Backend: get_analytics_summary()
    ↓
MongoDB aggregation (no user filter)
    ↓
Returns GLOBAL impact metrics
    ↓
Frontend displays: GLOBAL food saved, GLOBAL people fed, GLOBAL trees
    ↓
Inspires users to join the community
```

## Key Features

✅ **Personalized Analytics**
- Each user sees only their own impact
- Motivates individual contribution
- Clear "Your Impact" messaging

✅ **Global Impact Display**
- Login page shows community-wide progress
- Inspires potential members
- Transparent, public data

✅ **Non-Odd Placeholder**
- Analytics gracefully loads after page render
- Loading spinner indicates data coming
- Card layout integrates naturally with design
- Mobile-responsive (hidden on small screens)

✅ **Metric Changes**
- Emphasis on "Trees Planted" (more relatable than raw CO₂)
- Calculated as: 1 tree per 20 kg CO₂ saved
- People Fed, Food Saved remain for context

## Backward Compatibility

- Original `getAnalytics()` method still works
- Original `/api/analytics/summary` endpoint works without `user_specific` parameter
- Existing code won't break

## Testing Checklist

- [ ] Login page loads with global analytics visible (desktop)
- [ ] Analytics stats display correctly on login (Food, People, Trees)
- [ ] Login page works on mobile (analytics hidden, form visible)
- [ ] DonorDashboard shows user-specific analytics (not global)
- [ ] ReceiverDashboard shows user-specific analytics (not global)
- [ ] Stats only include user's own transactions
- [ ] Trees planted value shows correctly (carbon_saved / 20)
- [ ] Analytics gracefully handles no data (loading state → empty state)
- [ ] Global analytics accessible without authentication
- [ ] User-specific analytics require authentication

## Example Data

### Global Analytics (Login Page)
```json
{
  "total_food_saved_kg": 239,
  "total_people_fed": 1195,
  "total_carbon_saved": 597.5,
  "total_redistributions": 18,
  "total_trees_planted": 29
}
```

### User-Specific Analytics (Dashboard)
```json
{
  "total_food_saved_kg": 25,
  "total_people_fed": 125,
  "total_carbon_saved": 62.5,
  "total_redistributions": 2,
  "total_trees_planted": 3
}
```
Display: "You've saved 25 kg of food, fed 125 people, and planted 3 trees!"

## Files Modified

1. `backend/routes/analytics_routes.py` - Added endpoints & query param support
2. `backend/mongodb.py` - Added user-specific analytics method
3. `frontend/src/lib/api.ts` - Added API methods for user & global analytics
4. `frontend/src/components/mongodb/AnalyticsDashboard.tsx` - Use user-specific data
5. `frontend/src/pages/Login.tsx` - Complete redesign with global analytics showcase
