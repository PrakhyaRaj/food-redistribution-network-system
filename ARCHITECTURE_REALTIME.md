# Visual Architecture: Real-Time Dashboard Updates

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER (Frontend)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐   ┌──────────────────┐                    │
│  │ Transactions.tsx │   │  DashboardTabsTab │                   │
│  │                  │   │  ┌──────────────┐ │                   │
│  │ Listens for:     │   │  │ DonorDashbo..│ │                   │
│  │ • transaction_.. │   │  ├──────────────┤ │                   │
│  │ • transaction_.. │   │  │ ReceiverDash.│ │                   │
│  │ • match_found    │   │  └──────────────┘ │                   │
│  └─────────┬────────┘   └────────┬─────────┘ │                   │
│            │                     │            │                   │
│            └─────────┬───────────┘            │                   │
│                      │                        │                   │
│            ┌─────────▼──────────┐             │                   │
│            │  Socket.IO Events  │             │                   │
│            │  Emitted from BE   │             │                   │
│            └────────┬────────────┘             │                   │
│                     │                         │                   │
│            ┌────────▼────────────┐            │                   │
│            │ AnalyticsDashboard  │  ◄────────┤                   │
│            │ RouteOptimizer      │            │                   │
│            └────────┬────────────┘            │                   │
│                     │                         │                   │
│                     │      Call loadData()    │                   │
│                     └──────────────┬──────────┘                   │
│                                    │                              │
│                       ┌────────────▼──────────┐                   │
│                       │   HTTP REST API Calls │                   │
│                       │   Fetch Updated Data  │                   │
│                       └────────────┬──────────┘                   │
└────────────────────────────────────┼──────────────────────────────┘
                                     │
                    ┌────────────────▼──────────────┐
                    │     Network (HTTPS/WS)        │
                    └────────────────┬──────────────┘
                                     │
┌────────────────────────────────────▼──────────────────────────────┐
│                    SERVER (Backend - Flask)                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    Request Handlers                          │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                 │ │
│  │  │ POST /transact.. │  │ POST /food/add   │                 │ │
│  │  │ PUT /transact..  │  │ PUT /food/update │                 │ │
│  │  │ POST /requests   │  │ PUT /requests/.. │                 │ │
│  │  └────────┬─────────┘  └────────┬─────────┘                 │ │
│  │           │                     │                            │ │
│  │  ┌────────▼──────────────────────▼────────┐                 │ │
│  │  │  Database Operations (Create/Update)   │                 │ │
│  │  │  • PostgreSQL (transactions, food)     │                 │ │
│  │  │  • MongoDB (analytics)                 │                 │ │
│  │  └────────┬───────────────────────────────┘                 │ │
│  │           │                                                  │ │
│  │  ┌────────▼────────────────────────────────┐                │ │
│  │  │  Socket.IO Event Emission (NEW)         │                │ │
│  │  │  socketio.emit('transaction_created',..)│                │ │
│  │  │  socketio.emit('food_added', ...)       │                │ │
│  │  │  socketio.emit('request_updated', ...)  │                │ │
│  │  └────────┬────────────────────────────────┘                │ │
│  │           │                                                  │ │
│  │           └──── Broadcast to All Connected Clients          │ │
│  │                                                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Socket.IO Manager (sockets.py)                 │ │
│  │  • Manages WebSocket connections                            │ │
│  │  • Handles client authentication                            │ │
│  │  • Routes events to subscribed clients                      │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## 🔄 Real-Time Update Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         START                                    │
│              User Creates Transaction via API                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  Backend: POST /transactions/  │
        │  create_transaction()           │
        └────────────────┬───────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
    ┌──────────────────┐   ┌─────────────────┐
    │ Save to DB       │   │ Validate Data   │
    │ (PostgreSQL)     │   │                 │
    └────────┬─────────┘   └─────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │  Store in MongoDB Analytics  │
    │  (store_transaction_in_...)  │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────────┐
    │  Emit Socket.IO Events (NEW!)            │
    │  ┌─────────────────────────────────────┐ │
    │  │ To Donor:                           │ │
    │  │ socketio.emit('transaction_created',│ │
    │  │             data,                   │ │
    │  │             room=f'user_{donor_id}')│ │
    │  ├─────────────────────────────────────┤ │
    │  │ To Receiver:                        │ │
    │  │ socketio.emit('transaction_created',│ │
    │  │             data,                   │ │
    │  │             room=f'user_{receiver_)│ │
    │  ├─────────────────────────────────────┤ │
    │  │ To Everyone:                        │ │
    │  │ socketio.emit('transaction_created',│ │
    │  │             data,                   │ │
    │  │             broadcast=True)         │ │
    │  └─────────────────────────────────────┘ │
    └────────┬──────────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │  Return HTTP 201 Success Response    │
    │  { "transaction_id": 123 }           │
    └────────┬─────────────────────────────┘
             │
    ┌────────┴──────────────────────────────────┐
    │         WebSocket Network                  │
    │                                            │
    │     ┌──────────────────────────┐          │
    │     │ Socket.IO Event Broadcast │          │
    │     │ event: 'transaction_..    │          │
    │     │ data: {...transaction...} │          │
    │     └────────┬─────────────────┘          │
    │              │                             │
    └──────────────┼─────────────────────────────┘
                   │
        ┌──────────┴──────────┬────────────────┐
        │                     │                │
        ▼                     ▼                ▼
    ┌───────┐            ┌───────┐        ┌────────┐
    │ Client│            │Client │        │ Client │
    │   1   │            │  2    │        │   3    │
    │(Donor)│            │(Donor)│        │(Receiver)
    └───┬───┘            └───┬───┘        └────┬───┘
        │                    │                 │
        │ Event Listener:    │ Event Listener: │ Event Listener:
        │ newSocket.on('tr.. │ newSocket.on('tr│ newSocket.on('tr...
        │ loadTransactions() │ loadTransactions │ loadTransactions()
        │                    │ ()              │
        ▼                    ▼                 ▼
    ┌─────────────────────────────────────────────┐
    │    Frontend: Load Updated Transactions      │
    │    GET /transactions/user/{user_id}         │
    └────────────────┬────────────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────┐
    │  Backend: get_user_transactions()   │
    │  Query DB for latest transactions   │
    └────────────────┬────────────────────┘
                     │
                     ▼
    ┌──────────────────────────────────────┐
    │  Return HTTP 200 with Updated List   │
    │  [ { txn_id: 123, ... } ]            │
    └────────────────┬─────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────────────┐
    │   Frontend: Update State & Re-render        │
    │   setTransactions([...new data])            │
    │   Components re-render with new data        │
    └────────────────┬────────────────────────────┘
                     │
                     ▼
    ┌──────────────────────────────────────┐
    │    ✅ Dashboard Updated in Real-Time!│
    │    • Transactions list shows new txn  │
    │    • Analytics updated (kg/carbon)    │
    │    • Toast notification shown        │
    └──────────────────────────────────────┘
```

## 🎯 Event Mapping

```
Backend Route              Event Emitted           Affected Components
─────────────────────────────────────────────────────────────────────
POST /transactions/create  transaction_created     • Transactions.tsx
                                                  • DonorDashboard
                                                  • ReceiverDashboard
                                                  • AnalyticsDashboard
                                                  • RouteOptimizer

PUT /transactions/update   transaction_updated     • Transactions.tsx
                                                  • DonorDashboard
                                                  • ReceiverDashboard

POST /food/add             food_added              • DonorDashboard
                                                  • AnalyticsDashboard
                                                  • RouteOptimizer

PUT /food/update           food_updated            • DonorDashboard

POST /requests/add_req      request_created        • DonorDashboard
                                                  • ReceiverDashboard

PUT /requests/update       request_updated         • ReceiverDashboard

DELETE /requests/cancel    request_cancelled       • ReceiverDashboard
```

## 🔌 Socket.IO Connection Flow

```
┌──────────────────────────────────────────────┐
│          Frontend (Component Mount)          │
├──────────────────────────────────────────────┤
│                                              │
│  1. Get token from localStorage              │
│     token = localStorage.getItem('token')    │
│                                              │
│  2. Create Socket.IO connection              │
│     const socket = io('http://127.0.0.1..')  │
│                                              │
│  3. Send token in multiple ways              │
│     • query: { token }                       │
│     • auth: { token }                        │
│                                              │
│  4. Configure connection options             │
│     • transports: ['websocket', 'polling']   │
│     • reconnection: true                     │
│     • reconnectionAttempts: 5                │
│                                              │
└──────────────────┬───────────────────────────┘
                   │
                   ▼ WebSocket Connection
┌──────────────────────────────────────────────┐
│          Backend (sockets.py)                │
├──────────────────────────────────────────────┤
│                                              │
│  @socketio.on('connect')                     │
│  def handle_connect():                       │
│      # Extract token from multiple sources   │
│      token = request.args.get('token')       │
│      OR Authorization header                 │
│      OR auth param                           │
│                                              │
│      # Validate JWT token                    │
│      decoded = decode_token(token)           │
│      user_id = decoded.get('sub')            │
│                                              │
│      # Store in memory for broadcasting      │
│      connected_users[user_id] = request.sid  │
│                                              │
│      # Join user's room                      │
│      join_room(f"user_{user_id}")            │
│                                              │
│      # Emit connection confirmation          │
│      emit('connection_status', {             │
│          'status': 'connected'               │
│      })                                      │
│                                              │
└──────────────────┬───────────────────────────┘
                   │
                   ▼ Connection Established
┌──────────────────────────────────────────────┐
│    Frontend: Connection Status Confirmed     │
├──────────────────────────────────────────────┤
│                                              │
│  newSocket.on('connection_status', (data) => {
│      if (data.status === 'connected') {      │
│          console.log('✅ Connected')         │
│      }                                       │
│  })                                          │
│                                              │
│  Ready to receive real-time events! 🚀       │
│                                              │
└──────────────────────────────────────────────┘
```

## 📊 Data Sync Timeline

```
Time    Event                           Backend      Frontend      Dashboard
────────────────────────────────────────────────────────────────────────────
T+0ms   User clicks "Create Transaction"
        
T+50ms                                  HTTP POST
        
T+150ms                                 ✅ Data saved
                                        to DB
        
T+160ms                                 Socket.IO
                                        event
                                        emitted
        
T+200ms                                                Event
                                                       received
        
T+210ms                                                loadData()
                                                       called
        
T+260ms                                                HTTP GET
                                                       request
        
T+300ms                                                ✅ Data
                                                       received
        
T+320ms                                                                ✅ Dashboard
                                                                        updated
                                                                        visible
                                                                        
Total latency: ~320ms from action to visible update
```

## 🎯 Key Architecture Improvements

```
BEFORE (No Socket.IO Emission):
┌──────────┐
│ Create   │
│Transaction
└────┬─────┘
     │ API POST
     ▼
┌──────────┐
│ Backend  │
│ Saves DB │
└────┬─────┘
     │ HTTP 201
     ▼
┌──────────┐
│ Frontend │    ❌ Manual Refresh Needed
│ Keeps    │       to see changes
│ Old Data │
└──────────┘

AFTER (With Socket.IO Emission):
┌──────────┐
│ Create   │
│Transaction
└────┬─────┘
     │ API POST
     ▼
┌──────────────────────┐
│ Backend              │
│ • Saves DB           │
│ • Emits Socket.IO    │ ◄─── NEW!
│   event              │
└────┬──────────────────┘
     │
     ├─── HTTP 201          ┌──────────┐
     │                     │Frontend 1│
     │                     │Receives  │
     │                     │Event &   │
     │                     │Refreshes │
     │                     └──────────┘
     │
     ├─── WebSocket       ┌──────────┐
     │     'transaction    │Frontend 2│
     │      _created'      │Receives  │
     │                     │Event &   │
     │                     │Refreshes │
     │                     └──────────┘
     │
     └─── WebSocket       ┌──────────┐
           Broadcast       │Frontend 3│
                          │Receives  │
                          │Event &   │
                          │Refreshes │
                          └──────────┘

✅ Automatic updates for all clients!
```

---

**This architecture ensures real-time synchronization across all connected clients with minimal latency and network overhead.**
