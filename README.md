# 🍲 Food Redistribution Network System (FRNS)

A modern, full-stack platform connecting food donors with receivers to reduce waste and support communities. Features real-time matching, route optimization, analytics dashboard, and multi-role management.

---

## ✨ Key Features

### For Donors
- **Food Listing**: List surplus food with details (name, quantity, expiry date, location)
- **Image Uploads**: Add photos to food listings (MongoDB Base64 storage)
- **Request Matching**: View nearby food requests and accept matches
- **Route Optimization**: Automated delivery route planning with OSRM API
- **Transaction History**: Track donations and view statistics

### For Receivers
- **Food Browser**: Search and browse available food nearby
- **Request Creation**: Post food needs with requirements
- **Smart Matching**: Automatic donor-receiver matching based on location
- **Real-time Notifications**: Instant alerts for new matches via Socket.IO

### For Admins
- **User Management**: View, promote, or deactivate users
- **System Monitoring**: Track food listings, requests, and transactions
- **Analytics Dashboard**: Platform-wide statistics and insights
- **Activity Logs**: MongoDB-powered activity feed
- **Health Checks**: System status monitoring

### Advanced Features
- **Real-time Updates**: Socket.IO for instant notifications
- **Dual Database**: PostgreSQL (primary data) + MongoDB (analytics/images)
- **Geolocation**: Distance-based matching with Haversine formula
- **Route Planning**: OSRM API integration for optimal delivery routes
- **Analytics**: Food saved metrics, carbon impact, activity trends
- **Role-based Access**: JWT authentication with role synchronization

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0 with Flask-CORS
- **Database**: PostgreSQL 14+ (SQLAlchemy ORM)
- **NoSQL**: MongoDB 6+ (PyMongo)
- **Authentication**: JWT (Flask-JWT-Extended)
- **Real-time**: Flask-SocketIO
- **Route Optimization**: OSRM API + Haversine fallback
- **Migrations**: Alembic

### Frontend
- **Framework**: React 18 with TypeScript 5
- **Build Tool**: Vite 5
- **Routing**: React Router v6
- **Styling**: Tailwind CSS + shadcn/ui components
- **Charts**: Recharts
- **Real-time**: Socket.IO Client
- **State Management**: React Context API

### DevOps
- **Containerization**: Docker & Docker Compose
- **API Testing**: Postman collection included
- **Version Control**: Git

---

## 📋 Prerequisites

| Requirement | Version | Purpose |
|------------|---------|---------|
| **Node.js** | 18.x+ | Frontend runtime |
| **npm** | 9.x+ | Package management |
| **Python** | 3.10+ | Backend runtime |
| **PostgreSQL** | 14.x+ | Primary database |
| **MongoDB** | 6.x+ | Analytics & images (optional) |
| **Docker** | Latest | Database containerization |
| **Git** | Latest | Version control |

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd food-redistribution-network-system
```

### Step 2: Database Setup

#### Option A: Docker (Recommended - No PATH Issues)
```powershell
# Start both PostgreSQL and MongoDB
docker-compose up -d

# Verify containers are running
docker ps

# Expected: frns-postgres (PostgreSQL) and frns-mongo (MongoDB) containers
```

**Docker automatically creates:**
- PostgreSQL database `frns_db` on port 5432
- MongoDB database on port 27017
- Default credentials (postgres/postgres for PostgreSQL)

#### Option B: Manual PostgreSQL Installation
```bash
# Windows (using PostgreSQL installer)
# 1. Download from https://www.postgresql.org/download/windows/
# 2. Install with default settings
# 3. Create database:
createdb frns_db

# Linux/Mac
sudo apt install postgresql  # or brew install postgresql
sudo -u postgres createdb frns_db
```

#### Option C: MongoDB Setup (Optional but Recommended)
**Using Docker (Easiest):**
```bash
docker run -d -p 27017:27017 --name mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=example \
  mongo:latest
```

**Or using Docker Compose:**
```bash
docker-compose -f docker-compose.mongo.yml up -d
```

**Verify MongoDB:**
```bash
docker ps --filter "name=mongo"
docker logs mongodb --tail 20
```

**⚠️ Without MongoDB:** The app still works with PostgreSQL only, but you'll lose:
- Route optimization caching
- Food image uploads
- Advanced analytics
- Activity logs

### Step 3: Backend Setup

#### a) Navigate to Backend
```bash
cd backend
```

#### b) Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### c) Install Dependencies
```bash
pip install -r requirements.txt
```

#### d) Configure Environment Variables
Create `backend/.env` file:

```env
# PostgreSQL Database (Docker)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/frns_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Flask Environment
FLASK_ENV=development
FLASK_DEBUG=True

# MongoDB (Optional - Docker)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=frns_db

# File Uploads
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# CORS (adjust for production)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**For Manual PostgreSQL:**
```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/frns_db
```

**For MongoDB with Authentication:**
```env
MONGO_URI=mongodb://root:example@localhost:27017/frns_db?authSource=admin
```

#### e) Initialize Database
```bash
# Run migrations to create tables
flask db upgrade

# Or if above fails:
python -m flask db upgrade
```

#### f) Run Backend Server
```bash
python app.py
```

**Backend will run at:** http://127.0.0.1:5000

**Expected logs:**
```
✅ PostgreSQL connected successfully
✅ MongoDB connected successfully (or ⚠️ Using SQL fallback if not available)
✅ Socket.IO initialized
* Running on http://127.0.0.1:5000
```

### Step 4: Frontend Setup

#### a) Navigate to Frontend (New Terminal)
```bash
cd frontend
```

#### b) Install Dependencies
```bash
npm install
```

#### c) Configure Environment Variables
Create `frontend/.env.local`:

```env
VITE_API_URL=http://127.0.0.1:5000
VITE_SOCKET_URL=http://127.0.0.1:5000
```

#### d) Run Development Server
```bash
npm run dev
```

**Frontend will run at:** http://localhost:5173

---

## 📁 Project Structure

```
food-redistribution-network-system/
├── backend/
│   ├── app.py                      # Flask application entry point
│   ├── auth.py                     # Authentication & JWT routes
│   ├── config.py                   # Configuration management
│   ├── extensions.py               # Flask extensions (db, jwt, socketio)
│   ├── models.py                   # SQLAlchemy models (User, FoodItem, Request, Transaction)
│   ├── mongodb.py                  # MongoDB service layer
│   ├── mongo_client.py             # MongoDB client initialization
│   ├── sockets.py                  # Socket.IO event handlers
│   ├── validation.py               # Input validation utilities
│   ├── notifications.py            # Notification management
│   ├── requirements.txt            # Python dependencies
│   ├── routes/
│   │   ├── admin_routes.py         # Admin dashboard endpoints
│   │   ├── analytics_routes.py     # Analytics & statistics
│   │   ├── feedback_routes.py      # Feedback management
│   │   ├── food_routes.py          # Food CRUD + matching logic
│   │   ├── food_images_routes.py   # Image upload/retrieval
│   │   ├── mongodb_routes.py       # MongoDB utilities
│   │   ├── request_routes.py       # Request CRUD
│   │   ├── route_routes.py         # Route optimization
│   │   ├── transaction_routes.py   # Transaction management
│   │   └── user_routes.py          # User management
│   ├── services/
│   │   ├── activity_logger.py      # MongoDB activity logging
│   │   ├── analytics_service.py    # Analytics calculations
│   │   ├── feedback_service.py     # Feedback processing
│   │   ├── geo_service.py          # Geolocation utilities
│   │   ├── matching_service.py     # Donor-receiver matching
│   │   ├── notification_service.py # Notification dispatch
│   │   └── route_optimizer.py      # OSRM API integration
│   └── migrations/                 # Alembic database migrations
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── AdminDashboard.tsx      # Admin panel
│   │   │   │   ├── DonorDashboard.tsx      # Donor view
│   │   │   │   └── ReceiverDashboard.tsx   # Receiver view
│   │   │   ├── food/
│   │   │   │   ├── FoodList.tsx            # Food listings grid
│   │   │   │   └── FoodForm.tsx            # Add/edit food
│   │   │   ├── requests/
│   │   │   │   ├── RequestList.tsx         # Request listings
│   │   │   │   └── MatchedFoods.tsx        # Matched items
│   │   │   ├── mongodb/
│   │   │   │   ├── NotificationCenter.tsx  # Real-time notifications
│   │   │   │   ├── AnalyticsDashboard.tsx  # Analytics charts
│   │   │   │   ├── FeedbackInsights.tsx    # Feedback statistics
│   │   │   │   └── TransactionHistory.tsx  # Transaction logs
│   │   │   ├── ui/                         # shadcn/ui components
│   │   │   ├── LocationPicker.tsx          # Map-based location selector
│   │   │   ├── NotificationHandler.tsx     # Socket.IO client wrapper
│   │   │   └── ProtectedRoute.tsx          # Route authentication guard
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx             # Auth state & token management
│   │   ├── lib/
│   │   │   ├── api.ts                      # API client with auth headers
│   │   │   └── utils.ts                    # Utility functions
│   │   ├── pages/
│   │   │   ├── Login.tsx                   # Login page
│   │   │   ├── Register.tsx                # Registration
│   │   │   ├── Dashboard.tsx               # Main dashboard router
│   │   │   ├── AddFood.tsx                 # Add food form
│   │   │   ├── AddRequest.tsx              # Add request form
│   │   │   ├── MyFoods.tsx                 # User's food listings
│   │   │   ├── MyRequests.tsx              # User's requests
│   │   │   ├── AdminDashboard.tsx          # Admin panel
│   │   │   └── Profile.tsx                 # User profile
│   │   ├── App.tsx                         # Router configuration
│   │   └── main.tsx                        # Application entry point
│   ├── package.json                        # npm dependencies
│   ├── vite.config.ts                      # Vite configuration
│   └── tailwind.config.ts                  # Tailwind CSS configuration
│
├── FRNS_API_Postman_Collection.json        # API testing collection
├── docker-compose.yml                      # PostgreSQL + MongoDB setup
├── docker-compose.mongo.yml                # MongoDB-only setup
├── .gitignore                              # Git ignore rules
└── README.md                               # This file
```

---

## 🔐 Authentication & Authorization

### User Roles
| Role | Capabilities |
|------|-------------|
| **Donor** | List food, view requests, accept matches, track donations |
| **Receiver** | Create requests, browse food, accept matches, receive notifications |
| **Admin** | All above + user management, system monitoring, analytics |

### JWT Authentication Flow
1. User registers/logs in via `/auth/register` or `/auth/login`
2. Backend generates JWT access token (30-minute expiry)
3. Frontend stores token in `localStorage`
4. All API calls include `Authorization: Bearer <token>` header
5. Backend validates token and extracts user roles
6. Role-based access control enforced on protected routes

### Role Management
```python
# Promote user to admin via Python shell
from backend.app import app, db
from backend.models import User, Role

with app.app_context():
    admin_role = Role.query.filter_by(role_name='admin').first()
    if not admin_role:
        admin_role = Role(role_name='admin')
        db.session.add(admin_role)
    
    user = User.query.filter_by(email='admin@example.com').first()
    if user and admin_role not in user.roles:
        user.roles.append(admin_role)
        db.session.commit()
        print(f"✅ {user.email} promoted to admin")
```

---

## 🌐 API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | User login (returns JWT) | No |
| POST | `/auth/logout` | User logout | Yes |
| GET | `/auth/debug-token` | Validate token | Yes |

### Food Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/food/all` | List all available foods | Yes |
| POST | `/food` | Create food listing | Yes (Donor) |
| GET | `/food/my/:userId` | Get user's food listings | Yes |
| PUT | `/food/:foodId` | Update food listing | Yes (Owner/Admin) |
| DELETE | `/food/:foodId` | Delete food listing | Yes (Owner/Admin) |
| GET | `/food/nearby` | Find nearby food items | Yes (Receiver) |
| POST | `/food/:foodId/images` | Upload food image | Yes (Owner) |
| GET | `/food/:foodId/images` | Get food images | Yes |

### Requests
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/requests/all` | List all requests | Yes |
| POST | `/requests` | Create food request | Yes (Receiver) |
| GET | `/requests/my/:userId` | Get user's requests | Yes |
| PUT | `/requests/:requestId` | Update request | Yes (Owner/Admin) |
| DELETE | `/requests/:requestId` | Delete request | Yes (Owner/Admin) |
| GET | `/food/requests/nearby` | Find nearby requests | Yes (Donor) |

### Transactions
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/transactions` | Create transaction | Yes |
| GET | `/transactions/user/:userId` | User's transactions | Yes |
| PUT | `/transactions/:txnId/status` | Update status | Yes |
| POST | `/transactions/:txnId/complete` | Mark complete | Yes |
| GET | `/transactions/:txnId` | Transaction details | Yes |

### Admin Dashboard
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/dashboard/summary` | System metrics | Admin |
| GET | `/api/admin/users` | List all users (paginated) | Admin |
| GET | `/api/admin/users/:userId` | User details | Admin |
| PUT | `/api/admin/users/:userId/role` | Update user roles | Admin |
| DELETE | `/api/admin/users/:userId` | Deactivate user | Admin |
| GET | `/api/admin/foods` | List all foods (paginated) | Admin |
| DELETE | `/api/admin/foods/:foodId` | Delete food item | Admin |
| GET | `/api/admin/requests` | List all requests (paginated) | Admin |
| DELETE | `/api/admin/requests/:requestId` | Delete request | Admin |
| GET | `/api/admin/transactions` | List all transactions | Admin |
| GET | `/api/admin/statistics/food-types` | Food type statistics | Admin |
| GET | `/api/admin/statistics/daily-activity` | Activity timeline | Admin |
| GET | `/api/admin/health` | System health check | Admin |

### Analytics
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/analytics/summary` | User-specific analytics | Yes |
| GET | `/api/analytics/global-summary` | Platform-wide statistics | Yes |

### MongoDB Features
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/mongodb/notifications` | Get notifications | Yes |
| POST | `/api/mongodb/notifications/:id/read` | Mark notification read | Yes |
| GET | `/logs/activities` | Activity feed | Yes |
| POST | `/feedback` | Submit feedback | Yes |
| GET | `/feedback` | Get feedback | Admin |

### Route Optimization
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/routes/optimize` | Calculate optimal route | Yes |
| GET | `/api/routes/:userId` | Get user's routes | Yes |

---

## 🧪 API Testing with Postman

### Setup
1. Import `FRNS_API_Postman_Collection.json` into Postman
2. Set environment variable:
   - `base_url` = `http://127.0.0.1:5000`

### Authentication Workflow

#### Step 1: Register User
```http
POST {{base_url}}/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "Test@1234",
  "name": "Test User",
  "phone": "1234567890",
  "location_lat": 40.7128,
  "location_long": -74.0060,
  "roles": ["receiver"]
}
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "message": "User registered successfully"
}
```

#### Step 2: Add Token to Requests
**Method 1: Bearer Token (Recommended)**
1. Go to **Authorization** tab
2. Select **Bearer Token** type
3. Paste `access_token` value

**Method 2: Manual Header**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Step 3: Test Protected Endpoint
```http
GET {{base_url}}/food/all
Authorization: Bearer <your-token>
```

### Generate Test Token (Alternative)
```bash
cd backend
python
```
```python
from backend.app import app
from flask_jwt_extended import create_access_token

with app.app_context():
    token = create_access_token(identity={'user_id': 1, 'roles': ['donor', 'receiver']})
    print(f"Token: {token}")
```

---

## 🐛 Troubleshooting

### 1. Database Connection Errors

#### PostgreSQL Not Found
```bash
# Verify PostgreSQL is running
docker ps --filter "name=postgres"

# If not running:
docker-compose up -d

# Check logs:
docker logs frns-postgres
```

#### Database Doesn't Exist
```bash
# Using Docker:
docker exec -it frns-postgres psql -U postgres -c "CREATE DATABASE frns_db;"

# Using local PostgreSQL:
createdb frns_db
```

#### Migration Errors
```bash
cd backend
flask db upgrade

# If migrations folder is corrupt:
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 2. MongoDB Connection Issues

#### MongoDB Not Running
```bash
# Check status:
docker ps --filter "name=mongo"

# Start MongoDB:
docker start mongodb
# Or create new container:
docker run -d -p 27017:27017 --name mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=example \
  mongo:latest
```

#### Verify Connection
```python
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
print('Connected:', client.admin.command('ping'))
```

**⚠️ App continues without MongoDB:** If MongoDB is unavailable, the app falls back to PostgreSQL-only mode. Check backend logs for:
```
⚠️ MongoDB not connected, using SQL fallback
```

### 3. Route Optimization Not Showing

#### Check Database Column
```sql
-- Connect to PostgreSQL:
psql -U postgres -d frns_db

-- Check if route_data column exists:
SELECT column_name FROM information_schema.columns 
WHERE table_name='transactions' AND column_name='route_data';

-- If missing, add it:
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS route_data JSON;
```

#### Verify OSRM API
```bash
# Check backend logs for:
✅ OSRM API: Distance=14.49km, Duration=20.0min
```

### 4. Food Images Not Uploading

**Checklist:**
- ✅ MongoDB is running (`docker ps --filter "name=mongo"`)
- ✅ Backend logs show: `✅ MongoDB connected successfully`
- ✅ Check collection exists: `db.food_images.countDocuments()`
- ✅ File size < 16MB (`MAX_CONTENT_LENGTH` in `.env`)

### 5. 403 Unauthorized Errors

#### Invalid or Missing Token
```bash
# Generate fresh token:
cd backend
python
```
```python
from backend.app import app
from flask_jwt_extended import create_access_token

with app.app_context():
    token = create_access_token(identity={
        'user_id': 1,
        'email': 'test@example.com',
        'roles': ['donor', 'receiver', 'admin']
    })
    print(f"Token: {token}")
```

#### Token Expired
- Tokens expire after 30 minutes (default)
- Login again to get a fresh token
- Adjust expiry in `config.py`: `JWT_ACCESS_TOKEN_EXPIRES`

### 6. Socket.IO Connection Failed

**Frontend Not Connecting:**
1. Verify backend is running: http://127.0.0.1:5000
2. Check `VITE_SOCKET_URL` in `frontend/.env.local`
3. Ensure CORS allows frontend origin in `backend/config.py`
4. Open browser console (F12) → check for Socket.IO errors

**Common Error:**
```
Socket.IO connection failed: net::ERR_CONNECTION_REFUSED
```
**Fix:** Start backend server (`python app.py`)

### 7. Frontend Build Errors

#### Module Not Found
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Vite Cache Issues
```bash
rm -rf .vite
npm run dev
```

#### TypeScript Errors
```bash
# Verify tsconfig.json exists
npm run build  # Check for type errors
```

### 8. Docker Issues

#### Containers Not Starting
```bash
# View logs:
docker-compose logs

# Restart containers:
docker-compose down
docker-compose up -d
```

#### Port Already in Use
```bash
# Kill process on port 5432 (PostgreSQL):
# Windows:
netstat -ano | findstr :5432
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5432 | xargs kill -9
```

---

## 📊 Docker Management

### Quick Commands

#### Start All Services
```bash
docker-compose up -d
```

#### Check Status
```bash
docker-compose ps
```

#### View Logs
```bash
# All services:
docker-compose logs

# Specific service:
docker logs frns-postgres --tail 50
docker logs frns-mongo --tail 50
```

#### Stop Services
```bash
docker-compose down
```

#### Restart Services
```bash
docker-compose restart
```

#### Access Database Shells

**PostgreSQL:**
```bash
docker exec -it frns-postgres psql -U postgres -d frns_db
```

**MongoDB:**
```bash
docker exec -it frns-mongo mongosh -u root -p example --authenticationDatabase admin
```

### MongoDB Commands in Shell
```javascript
// Switch to database
use frns_db

// View collections
show collections

// Query transactions
db.transactions.find().limit(5).pretty()

// Count documents
db.food_images.countDocuments()
db.notifications.countDocuments()

// View recent activities
db.activities.find().sort({timestamp: -1}).limit(10).pretty()
```

### PostgreSQL Commands
```sql
-- View tables
\dt

-- View transactions with routes
SELECT txn_id, donor_id, receiver_id, route_data 
FROM transactions 
WHERE route_data IS NOT NULL 
LIMIT 10;

-- Count by status
SELECT status, COUNT(*) 
FROM transactions 
GROUP BY status;

-- View users and roles
SELECT u.user_id, u.email, u.name, r.role_name 
FROM users u 
LEFT JOIN user_roles ur ON u.user_id = ur.user_id 
LEFT JOIN roles r ON ur.role_id = r.role_id;
```

---

## 🚢 Production Deployment

### Environment Variables (Production)
```env
# Security
JWT_SECRET_KEY=<generate-strong-random-key-256-bits>
FLASK_ENV=production
FLASK_DEBUG=False

# Database
DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:5432/<database>?sslmode=require
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Uploads
MAX_CONTENT_LENGTH=16777216

# Session
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### Backend Deployment

#### Using Gunicorn (Recommended)
```bash
pip install gunicorn

# Production server with 4 workers:
gunicorn -w 4 -b 0.0.0.0:5000 --worker-class eventlet "backend.app:app"
```

#### Using Docker
```dockerfile
# Dockerfile (backend)
FROM python:3.10-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--worker-class", "eventlet", "backend.app:app"]
```

### Frontend Deployment

#### Build for Production
```bash
cd frontend
npm run build
```

**Output:** `frontend/dist/` directory

#### Serve with Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        root /var/www/frns/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Checklist
- [ ] Change `JWT_SECRET_KEY` to cryptographically secure random value
- [ ] Use HTTPS in production (Let's Encrypt SSL)
- [ ] Restrict CORS to specific domains (remove `*`)
- [ ] Enable rate limiting (Flask-Limiter)
- [ ] Set secure cookie flags (`SESSION_COOKIE_SECURE=True`)
- [ ] Use environment-specific configs (`.env.production`)
- [ ] Enable database connection pooling
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Implement logging (rotation, aggregation)
- [ ] Use secrets management (AWS Secrets Manager, HashiCorp Vault)

---

## 💡 Key Implementation Details

### Route Optimization
- **Primary**: OSRM API for real road network routing
- **Fallback**: Haversine formula for distance calculation
- **Storage**: Route data (distance, duration, geometry) stored in PostgreSQL `transactions.route_data` JSON column
- **Caching**: MongoDB stores route calculations for analytics

### Food Image Storage
- **Method**: Base64 encoding in MongoDB `food_images` collection
- **Fields**: `food_id`, `image_data` (Base64), `content_type`, `uploaded_at`
- **Limit**: 16MB per image (`MAX_CONTENT_LENGTH`)
- **Retrieval**: `/api/food/:foodId/images` endpoint returns image array

### Real-time Notifications
- **Transport**: Socket.IO with WebSocket/long-polling fallback
- **Events**: `new_match`, `transaction_update`, `new_notification`
- **Client**: React component with `NotificationHandler`
- **Server**: `backend/sockets.py` handles event broadcasting

### Matching Algorithm
1. Calculate distance between donor/receiver using Haversine
2. Filter food items within configurable radius (default: 50km)
3. Sort by proximity and food availability
4. Return top matches with distance metadata

### Analytics Calculations
- **Food Saved**: Sum of completed transaction quantities
- **People Fed**: Count of unique receivers in completed transactions
- **Carbon Impact**: Estimated CO₂ saved based on food weight
- **Activity Trends**: MongoDB aggregation pipeline for daily/weekly stats

---

## 🎯 Common Use Cases

### Use Case 1: Donor Lists Food
1. Login as donor
2. Navigate to "Add Food" or click "+" button
3. Fill form: name, quantity, expiry date, location
4. Optionally upload image
5. Submit → Food listed as "available"
6. View nearby requests for matching

### Use Case 2: Receiver Requests Food
1. Login as receiver
2. Navigate to "Add Request"
3. Specify food type, quantity, location
4. Submit → Request created
5. Browse available food or wait for matches
6. Accept match → Transaction created

### Use Case 3: Admin Monitors Platform
1. Login with admin account
2. Navigate to Admin Dashboard
3. View system metrics: total users, food listings, transactions
4. Manage users: promote roles, deactivate accounts
5. View statistics: food types, daily activity trends
6. Export data for reporting

### Use Case 4: Complete Transaction
1. Donor accepts match → Transaction status: "pending"
2. Route optimization calculates delivery route
3. Both parties receive notification
4. Status updates: "in_progress" → "completed"
5. Feedback prompt appears
6. Analytics updated with transaction data

---

## 🏃 Quick Start Commands

### Daily Development Workflow
```bash
# Terminal 1: Start databases (if using Docker)
docker-compose up -d

# Terminal 2: Backend
cd backend
python app.py

# Terminal 3: Frontend
cd frontend
npm run dev

# Access application:
# - Frontend: http://localhost:5173
# - Backend: http://127.0.0.1:5000
# - MongoDB: mongodb://localhost:27017
# - PostgreSQL: postgresql://localhost:5432/frns_db
```

### Database Management
```bash
# PostgreSQL
docker exec -it frns-postgres psql -U postgres -d frns_db

# MongoDB Shell
docker exec -it frns-mongo mongosh -u root -p example --authenticationDatabase admin

# View transactions with routes
SELECT * FROM transactions WHERE route_data IS NOT NULL;

# MongoDB collections
use frns_db
show collections
db.transactions.find().pretty()
```

### Testing API
```bash
# Health check
curl http://localhost:5000/api/admin/health

# Register user (get token)
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@1234","name":"Test User","phone":"1234567890","location_lat":40.7128,"location_long":-74.0060,"roles":["receiver"]}'

# Use token in subsequent requests
curl http://localhost:5000/food/all \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📝 Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| User Authentication | ✅ Working | JWT with role-based access |
| Food Listings CRUD | ✅ Working | Full create/read/update/delete |
| Request Management | ✅ Working | Full CRUD with matching |
| Transaction Flow | ✅ Working | Pending → In Progress → Completed |
| Route Optimization | ✅ Working | OSRM API integration verified |
| Food Image Upload | ✅ Working | MongoDB Base64 storage |
| Real-time Notifications | ✅ Working | Socket.IO bidirectional communication |
| Admin Dashboard | ✅ Working | User/food/request management |
| Analytics | ✅ Working | User & global statistics |
| MongoDB Integration | ✅ Working | Analytics, images, activity logs |
| Location-based Matching | ✅ Working | Haversine distance calculation |
| Role Synchronization | ✅ Working | Auto-sync every 30 seconds |

---

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m "Add new feature"`
4. Push to branch: `git push origin feature/new-feature`
5. Open a pull request

---

## 📄 License
All rights reserved. Internal project for food redistribution network.

---

## 📞 Support

### Resources
- **Backend Logs**: Check terminal running `python app.py`
- **Frontend Logs**: Browser console (F12)
- **Database Logs**: `docker logs frns-postgres` / `docker logs frns-mongo`
- **API Collection**: Import `FRNS_API_Postman_Collection.json` for testing

### Health Check Endpoints
- Backend: http://127.0.0.1:5000/api/admin/health
- Frontend: http://localhost:5173 (should load login page)

---

## 🛣️ Roadmap

### Planned Features
- [ ] Mobile app (React Native)
- [ ] SMS/Email notifications
- [ ] Multi-language support (i18n)
- [ ] Payment integration for delivery costs
- [ ] User rating system (5-star reviews)
- [ ] Advanced route optimization with real-time traffic
- [ ] Automated expiry alerts (cron jobs)
- [ ] Bulk food upload via CSV
- [ ] Public API with rate limiting
- [ ] Data export (CSV/PDF reports)
- [ ] Dark mode theme
- [ ] Progressive Web App (PWA)
- [ ] QR code generation for transactions
- [ ] Gamification (badges, leaderboards)

---

Built with ❤️ for reducing food waste and supporting communities

**Version:** 1.0.0  
**Last Updated:** 2024  
**Maintained by:** FRNS Development Team
