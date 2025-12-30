# FRNS Frontend

React + TypeScript + Vite frontend for the Food Redistribution Network System.

## Overview

Modern, responsive web application providing role-based interfaces for donors, receivers, and administrators. Features real-time notifications, interactive dashboards, analytics visualizations, and seamless API integration.

## Tech Stack

- **Framework**: React 18
- **Language**: TypeScript 5
- **Build Tool**: Vite 5
- **Routing**: React Router v6
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Charts**: Recharts
- **Real-time**: Socket.IO Client
- **HTTP Client**: Fetch API with custom wrapper
- **State Management**: React Context API
- **Forms**: React Hook Form (where applicable)

## Prerequisites

- Node.js 18+ and npm 9+
- Backend API running at `http://127.0.0.1:5000`
- Modern browser (Chrome, Firefox, Safari, Edge)

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment
Create `.env.local` file:
```env
VITE_API_URL=http://127.0.0.1:5000
VITE_SOCKET_URL=http://127.0.0.1:5000
```

### 3. Run Development Server
```bash
npm run dev
```
Access at: http://localhost:5173

## Project Structure

```
frontend/
├── node_modules/
├── public/
├── src/
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── DonorDashboard.tsx
│   │   │   └── ReceiverDashboard.tsx
│   │   ├── food/
│   │   │   ├── FoodList.tsx
│   │   │   └── FoodNotes.tsx
│   │   ├── home/
│   │   │   └── Homepage.tsx
│   │   ├── mongodb/
│   │   │   ├── AnalyticsSummary.tsx
│   │   │   ├── MongoDBCard.tsx
│   │   │   ├── NotificationHandler.tsx
│   │   │   ├── RouteOpt.tsx
│   │   │   ├── TransactionHistory.tsx
│   │   │   └── submitfeedback.tsx
│   │   ├── profile/
│   │   │   └── ProfileFeedback.tsx
│   │   ├── requests/
│   │   │   ├── MatchedFoods.tsx
│   │   │   └── RequestList.tsx
│   │   ├── ui/
│   │   │   └── ... (UI components)
│   │   ├── AnalyticsSummary.tsx
│   │   ├── NavLink.tsx
│   │   ├── NotificationHandler.tsx
│   │   ├── ProfileButton.tsx
│   │   └── ProtectedRoute.tsx
│   ├── contexts/
│   │   └── AuthContext.tsx
│   ├── hooks/
│   │   ├── useFoodImages.ts
│   │   └── useFoodNotes.ts
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   └── AdminDashboard.tsx
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── .env.local
├── components.json
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── package.json
```

## Key Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (donor/receiver/admin)
- Protected routes with automatic redirection
- Token storage in localStorage
- Auto role synchronization from backend

### Dashboards
#### Donor Dashboard
- Food listings management (CRUD)
- Nearby requests viewer
- Matched foods notification
- Route optimization interface
- Transaction history
- Personal analytics

#### Receiver Dashboard
- Request creation and management
- Available food browser
- Match notifications
- Transaction tracking
- Feedback submission
- Personal analytics

#### Admin Dashboard
- System overview metrics
- User management (paginated)
- Food management (paginated)
- Request oversight
- Transaction monitoring
- Analytics visualizations:
  - All-time daily activity chart
  - Food type distribution
  - System health status

### Real-time Features
- Socket.IO integration
- Live match notifications
- Status update alerts
- Connection status indicator
- Automatic reconnection
- JWT-authenticated WebSocket

### Analytics & Insights
- MongoDB-backed analytics
- Interactive charts (Recharts)
- Notification center
- Activity feed
- Feedback insights
- Transaction history

## Components Guide

### Core Components
#### AuthContext (`contexts/AuthContext.tsx`)
```typescript
const { userId, roles, login, logout, isAuthenticated } = useAuth();
```
**Features:**
- Manages authentication state
- Stores JWT token
- Syncs roles every 30 seconds
- Provides login/logout functions

#### ProtectedRoute (`components/ProtectedRoute.tsx`)
```typescript
<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>
```
Redirects to `/login` if not authenticated.

#### NotificationHandler (`components/NotificationHandler.tsx`)
```typescript
// Automatically connects Socket.IO on mount
// Displays toast notifications
// Manages connection state
```

### Dashboard Components
#### DonorDashboard
- Lists donor's food items
- Shows nearby requests
- Displays matched foods with real-time updates
- Route optimization tool
- Transaction history

#### ReceiverDashboard
- Shows user's requests
- Browse available foods
- View matched items
- Submit feedback
- Transaction tracking

#### AdminDashboard
- 6 tabs: Overview, Users, Foods, Requests, Transactions, Analytics
- Paginated tables with actions
- Charts for data visualization
- System health monitoring
- All-time activity graph

### MongoDB Components
Located in `components/mongodb/`:

- **NotificationCenter**: Real-time notification feed with read/unread status
- **AnalyticsDashboard**: Key metrics cards and user-specific statistics
- **TransactionHistory**: Chronological transaction log with status badges
- **FeedbackInsights**: Average ratings and feedback distribution
- **ActivitiesFeed**: Real-time activity stream with action types
- **FoodNotesManager**: Food item notes management

## API Integration

### API Client (`lib/api.ts`)
```typescript
import { api } from '@/lib/api';

// Authentication
const response = await api.auth.login(email, password);

// Food operations
const foods = await api.food.getAll();
await api.food.create(foodData);

// Admin operations
const summary = await api.get('/api/admin/dashboard/summary');

// Generic HTTP methods
const data = await api.get(url);
await api.post(url, data);
await api.put(url, data);
await api.delete(url);
```

**Features:**
- Automatic JWT token injection
- Error handling with toast notifications
- Request/response logging in development
- Type-safe responses

### API Methods

#### Authentication
- `api.auth.register(userData)`
- `api.auth.login(email, password)`
- `api.auth.logout()`

#### Food
- `api.food.getAll()`
- `api.food.create(foodData)`
- `api.food.getMyFood(userId)`
- `api.food.getNearby()`
- `api.food.update(foodId, data)`
- `api.food.delete(foodId)`

#### Requests
- `api.requests.getAll()`
- `api.requests.create(requestData)`
- `api.requests.getMyRequests(userId)`
- `api.requests.getNearby()`

#### Transactions
- `api.transactions.create(data)`
- `api.transactions.getUserTransactions(userId)`
- `api.transactions.updateStatus(txnId, status)`
- `api.transactions.complete(txnId)`

#### MongoDB Features
- `api.mongodb.getNotifications()`
- `api.mongodb.markAsRead(notificationId)`
- `api.mongodb.getActivities()`
- `api.mongodb.submitFeedback(data)`

## Routing

### Public Routes
- `/` - Landing page (redirects to `/login` or `/dashboard`)
- `/login` - Login page
- `/register` - Registration page

### Protected Routes
- `/dashboard` - Main dashboard (role-based view)
- `/admin/dashboard` - Admin panel (admin only)

### Route Configuration (`App.tsx`)
```typescript
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />
  <Route
    path="/dashboard"
    element={
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    }
  />
  <Route
    path="/admin/dashboard"
    element={
      <ProtectedRoute>
        <AdminDashboard />
      </ProtectedRoute>
    }
  />
</Routes>
```

### Navigation
```typescript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();
navigate('/dashboard');
navigate('/admin/dashboard');
```

## State Management

### Global State (AuthContext)
- User ID
- User roles
- Authentication status
- Login/logout functions

### Local State (useState)
- Component-specific data
- Form inputs
- Loading states
- Error messages

### Real-time State (Socket.IO)
- Notifications
- Match updates
- Status changes

## Styling

### Tailwind CSS
Utility-first CSS framework with custom configuration:
```typescript
<div className="bg-primary text-white p-4 rounded-lg shadow-md">
  <h1 className="text-2xl font-bold">Title</h1>
  <p className="text-sm text-muted-foreground">Description</p>
</div>
```

### UI Components
Pre-built, accessible components:
```typescript
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

<Button variant="outline" size="lg">Click Me</Button>
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

### Custom Styles
Global styles in `index.css`:
```css
@layer base {
  :root {
    --primary: 222.2 47.4% 11.2%;
    --secondary: 210 40% 96.1%;
    /* ... */
  }
}
```

## TypeScript Usage

### Type Safety
```typescript
// API response types
interface LoginResponse {
  success: boolean;
  access_token: string;
  user_id: number;
  roles: string[];
}

// Component props
interface FoodListProps {
  userId: number;
  onSelect?: (foodId: number) => void;
}

// State types
const [foods, setFoods] = useState<Food[]>([]);
```

### Type Imports
```typescript
import type { FC, ReactNode } from 'react';
```

## Charts & Visualizations

### Using Recharts
```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

<ResponsiveContainer width="100%" height={300}>
  <LineChart data={chartData}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="date" />
    <YAxis />
    <Tooltip />
    <Legend />
    <Line type="monotone" dataKey="foods" stroke="#3b82f6" />
    <Line type="monotone" dataKey="requests" stroke="#ef4444" />
  </LineChart>
</ResponsiveContainer>
```

### Chart Types Used
- Line charts (activity trends)
- Pie charts (food type distribution)
- Bar charts (statistics)

## Real-time Integration

### Socket.IO Setup
```typescript
// In NotificationHandler.tsx
import { io } from 'socket.io-client';

const socket = io(SOCKET_URL, {
  query: { token: localStorage.getItem('token') },
  transports: ['polling', 'websocket']
});

socket.on('notification', (data) => {
  toast(data.message);
});
```

### Event Handlers
```typescript
socket.on('connect', () => {
  console.log('Connected to Socket.IO');
});

socket.on('notification', (notification) => {
  // Handle notification
});

socket.on('match_found', (match) => {
  // Handle match
});

socket.on('disconnect', () => {
  console.log('Disconnected');
});
```

## Development

### Running Development Server
```bash
npm run dev
# or specify port
npm run dev -- --port 8080
```

### Environment Variables
#### Available Variables
```env
VITE_API_URL=http://127.0.0.1:5000
VITE_SOCKET_URL=http://127.0.0.1:5000
```

#### Accessing in Code
```typescript
const API_URL = import.meta.env.VITE_API_URL;
const SOCKET_URL = import.meta.env.VITE_SOCKET_URL;
```
**Note:** Variables must start with `VITE_` to be exposed to client.

## Deployment

### Static Hosting (Vercel, Netlify)
```bash
npm run build
# Deploy dist/ folder
```

### Environment Variables for Production
```env
VITE_API_URL=https://api.yourdomain.com
VITE_SOCKET_URL=https://api.yourdomain.com
```

## Troubleshooting

### Common Issues

#### 1. CORS Errors
```
Access to fetch at 'http://127.0.0.1:5000' from origin 'http://localhost:5173' has been blocked
```
**Solution:** Ensure backend CORS allows origin `http://localhost:5173`

#### 2. Socket.IO Connection Failed
```
WebSocket connection to 'ws://127.0.0.1:5000/' failed
```
**Solutions:**
1. Verify backend is running
2. Check `VITE_SOCKET_URL` in `.env.local`
3. Ensure JWT token is valid
4. Check browser console for errors

#### 3. 401 Unauthorized
```
API Error: Unauthorized
```
**Solutions:**
1. Login again to refresh token
2. Check token expiry (30 minutes default)
3. Verify token in localStorage: `localStorage.getItem('token')`

#### 4. Module Not Found
```
Cannot find module '@/components/...'
```
**Solution:** Check `tsconfig.json` has correct path aliases:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

#### 5. Build Errors
```bash
# Clear cache and rebuild
rm -rf node_modules .vite dist
npm install
npm run build
```

### Debug Tips

#### Enable Verbose Logging
In `lib/api.ts`, logging is already enabled in development:
```typescript
console.log('🔍 API Response:', response);
```

#### Check Network Requests
Open browser DevTools → Network tab → Filter by XHR/Fetch

#### Inspect State
```typescript
console.log('Auth state:', { userId, roles, isAuthenticated });
```

#### Socket.IO Debug
```typescript
socket.on('connect_error', (error) => {
  console.error('Socket.IO error:', error);
});
```