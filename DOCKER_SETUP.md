# 🐳 Docker Setup Guide - Complete Setup with Docker

This guide will help you set up **both PostgreSQL and MongoDB** using Docker, so you don't need to worry about PATH issues or manual database setup!

---

## ✅ Prerequisites

- **Docker Desktop** installed and running ([Download](https://www.docker.com/products/docker-desktop))
- Verify Docker is running:
  ```powershell
  docker --version
  docker ps
  ```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start All Databases with Docker

From the project root directory:

```powershell
# Start PostgreSQL and MongoDB
docker-compose up -d

# Verify both are running
docker ps
```

You should see two containers:
- `frns-postgres` (PostgreSQL)
- `frns-mongo` (MongoDB)

### Step 2: Wait for Databases to be Ready

```powershell
# Check if databases are healthy
docker-compose ps
```

Wait until both show "healthy" status (takes about 10-30 seconds).

### Step 3: Configure Backend

Update `backend/.env` file with these Docker database connections:

```env
# PostgreSQL (from Docker)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/frns_db

# MongoDB (from Docker)
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=frns_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-12345

# Flask Environment
FLASK_ENV=development
FLASK_DEBUG=True
```

**Note**: The database `frns_db` is automatically created by Docker!

---

## 📋 Complete Setup Steps

### 1. Start Docker Containers

```powershell
# From project root directory
docker-compose up -d
```

**What this does:**
- ✅ Creates PostgreSQL database `frns_db` automatically
- ✅ Creates MongoDB database
- ✅ Sets up all required credentials
- ✅ Exposes ports 5432 (PostgreSQL) and 27017 (MongoDB)

### 2. Verify Containers are Running

```powershell
docker ps
```

**Expected output:**
```
CONTAINER ID   IMAGE              STATUS          NAMES
xxxxxxxxxxxx   postgres:15-alpine Up X minutes    frns-postgres
xxxxxxxxxxxx   mongo:6            Up X minutes    frns-mongo
```

### 3. Check Database Health

```powershell
docker-compose ps
```

Wait until both show `healthy` status.

### 4. Configure Backend Environment

Create/update `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/frns_db
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=frns_db
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-12345
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Run Database Migrations

```powershell
cd backend

# Activate virtual environment
.\venv\Scripts\activate

# Run migrations (creates all tables)
flask db upgrade

# If that doesn't work:
python -m flask db upgrade
```

### 6. Start Backend

```powershell
# Still in backend directory with venv activated
python app.py
```

You should see:
```
🚀 Starting Food Redistribution Network with WebSocket support...
📡 WebSocket server running on: http://127.0.0.1:5000
```

### 7. Start Frontend (New Terminal)

```powershell
# New terminal window
cd frontend

# Install dependencies (first time only)
npm install

# Create .env.local if not exists
# Add: VITE_API_URL=http://127.0.0.1:5000
# Add: VITE_SOCKET_URL=http://127.0.0.1:5000

# Start frontend
npm run dev
```

---

## 🛠️ Docker Commands Reference

### Start Services
```powershell
docker-compose up -d          # Start in background
docker-compose up              # Start with logs visible
```

### Stop Services
```powershell
docker-compose stop            # Stop containers (keep data)
docker-compose down            # Stop and remove containers (keep data)
docker-compose down -v         # Stop and remove everything (DELETE DATA!)
```

### View Logs
```powershell
docker-compose logs            # All services
docker-compose logs postgres   # PostgreSQL only
docker-compose logs mongo      # MongoDB only
docker-compose logs -f         # Follow logs (live)
```

### Check Status
```powershell
docker-compose ps              # Container status
docker ps                      # All running containers
docker-compose ps              # Health status
```

### Restart Services
```powershell
docker-compose restart        # Restart all
docker-compose restart postgres  # Restart PostgreSQL only
```

### Access Databases (Optional)

**PostgreSQL:**
```powershell
# Connect to PostgreSQL container
docker exec -it frns-postgres psql -U postgres -d frns_db

# Or run SQL commands directly
docker exec -it frns-postgres psql -U postgres -d frns_db -c "SELECT version();"
```

**MongoDB:**
```powershell
# Connect to MongoDB container
docker exec -it frns-mongo mongosh

# Or run commands directly
docker exec -it frns-mongo mongosh --eval "db.adminCommand('ping')"
```

---

## 🔍 Troubleshooting

### Issue 1: "Port already in use"

**Error**: `Bind for 0.0.0.0:5432 failed: port is already allocated`

**Solution**: You have PostgreSQL running locally. Either:
- Stop local PostgreSQL service:
  ```powershell
  Stop-Service postgresql-x64-14  # Adjust version
  ```
- Or change Docker port in `docker-compose.yml`:
  ```yaml
  ports:
    - "5433:5432"  # Use 5433 instead
  ```
  Then update `DATABASE_URL` to use port 5433.

### Issue 2: "Cannot connect to database"

**Solution**: Wait for containers to be healthy:
```powershell
docker-compose ps
# Wait until both show "healthy"
```

### Issue 3: "Container keeps restarting"

**Solution**: Check logs:
```powershell
docker-compose logs postgres
docker-compose logs mongo
```

### Issue 4: "Permission denied" or "Access denied"

**Solution**: Make sure Docker Desktop is running and you have permissions.

### Issue 5: Want to Reset Everything

```powershell
# Stop and remove everything (DELETES ALL DATA!)
docker-compose down -v

# Start fresh
docker-compose up -d
```

---

## 📊 Database Credentials

### PostgreSQL (Docker)
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `frns_db`
- **Username**: `postgres`
- **Password**: `postgres`
- **Connection String**: `postgresql+psycopg2://postgres:postgres@localhost:5432/frns_db`

### MongoDB (Docker)
- **Host**: `localhost`
- **Port**: `27017`
- **Database**: `frns_db`
- **Username**: `root` (optional)
- **Password**: `example` (optional)
- **Connection String**: `mongodb://localhost:27017/`

---

## ✅ Verification Checklist

After running `docker-compose up -d`:

- [ ] `docker ps` shows both `frns-postgres` and `frns-mongo`
- [ ] `docker-compose ps` shows both as "healthy"
- [ ] Backend can connect (check backend terminal for "Using database...")
- [ ] Backend shows "✅ MongoDB connected successfully!" OR "⚠️ Running without MongoDB..."
- [ ] No errors in `docker-compose logs`

---

## 🎯 Complete Workflow

```powershell
# 1. Start databases
docker-compose up -d

# 2. Wait for healthy status
docker-compose ps

# 3. Setup backend (in backend directory)
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
python app.py

# 4. Setup frontend (new terminal)
cd frontend
npm install
npm run dev

# 5. Access application
# Frontend: http://localhost:5173
# Backend: http://127.0.0.1:5000
```

---

## 🛑 Stopping Everything

```powershell
# Stop containers (keeps data)
docker-compose stop

# Or stop and remove (keeps data volumes)
docker-compose down

# Or completely remove everything including data
docker-compose down -v
```

---

## 💡 Tips

1. **Keep Docker Desktop running** while developing
2. **Data persists** between restarts (stored in Docker volumes)
3. **Use `docker-compose logs -f`** to watch logs in real-time
4. **Use `docker-compose ps`** to check health status
5. **Backend and frontend** still run on your machine (not in Docker)

---

## 🆘 Still Having Issues?

1. **Docker not starting?**
   - Make sure Docker Desktop is installed and running
   - Check Windows WSL 2 is enabled (for Docker Desktop)

2. **Port conflicts?**
   - Stop local PostgreSQL/MongoDB services
   - Or change ports in `docker-compose.yml`

3. **Permission errors?**
   - Run PowerShell as Administrator
   - Check Docker Desktop has proper permissions

---

**That's it!** You now have both databases running in Docker. No need to worry about PATH issues or manual database setup! 🎉


