# Route Optimization Time Window Constraints

## Overview
Route optimization now enforces time window constraints based on transaction `pickup_date` field. This ensures deliveries can be completed within the scheduled time frame.

## Changes Made

### 1. RouteOptimizer Enhancement
**File**: `backend/services/route_optimizer.py`

#### New Parameter
- `pickup_date` (Optional[datetime]): Scheduled pickup datetime for time window enforcement

#### New Method: `_validate_time_window()`
Validates if a route can meet the scheduled pickup time window.

**Checks performed:**
1. **Past pickup detection**: Rejects if pickup_date is in the past
2. **Insufficient time**: Calculates if available time > required travel time + 30min buffer
3. **Too far future**: Warns if pickup is more than 7 days away
4. **Buffer calculation**: Returns time cushion available

**Returns:**
```python
{
    "valid": bool,           # True if time window is feasible
    "warning": str | None,   # Warning message if invalid or risky
    "buffer_hours": float    # Available cushion time (only if valid)
}
```

#### Updated Methods
- `optimize_route()`: Now accepts `pickup_date` parameter and validates time windows
- `_optimize_cluster_route()`: Supports time windows for multi-stop routes

### 2. API Endpoint Updates

#### `/api/routes/optimize` (POST)
**New Request Field:**
```json
{
  "pickup_points": [...],
  "delivery_points": [...],
  "constraints": {...},
  "pickup_date": "2025-12-25T10:00:00"  // ISO 8601 format
}
```

**Response Enhancement:**
```json
{
  "success": true,
  "route": {
    "scheduled_pickup": "2025-12-25T10:00:00",
    "time_window_warning": "Insufficient time window..." | null,
    ...
  }
}
```

#### `/api/routes/batch-optimize` (POST)
Each route in the batch can now include `pickup_date`:
```json
{
  "routes": [
    {
      "pickup_points": [...],
      "delivery_points": [...],
      "constraints": {...},
      "pickup_date": "2025-12-25T10:00:00"
    }
  ]
}
```

### 3. Transaction Flow Integration

#### Transaction Routes (`backend/routes/transaction_routes.py`)
- `/api/transactions/create`: Passes `pickup_date` from transaction to route optimizer

#### Request Routes (`backend/routes/request_routes.py`)
- `/api/requests/<id>/accept_food`: Uses transaction `pickup_date` for time validation
- `/api/requests/<id>/matches`: Uses request `deadline` as pickup target time
- `/api/food/<id>/requests`: Uses food `expiry_date` as pickup deadline constraint

#### Matching Service (`backend/services/matching_service.py`)
- `create_match_transaction()`: Passes transaction `pickup_date` to optimizer

## Time Window Validation Logic

### Required Time Calculation
```
required_time = estimated_travel_time + 0.5 hours (buffer)
```

### Validation Scenarios

| Scenario | Condition | Result | Warning Message |
|----------|-----------|--------|----------------|
| Past pickup | `pickup_date < now` | Invalid | "Pickup time is X hours in the past. Route cannot be fulfilled." |
| Insufficient time | `available_time < required_time` | Invalid | "Insufficient time window. Need Xh but only Yh available (shortage: Zh)" |
| Too far future | `available_time > 168h (7 days)` | Valid with warning | "Pickup scheduled X days in advance. Consider re-optimizing closer to pickup time." |
| Valid window | All checks pass | Valid | None |

## Usage Examples

### Example 1: Single Route Optimization with Time Window
```python
from datetime import datetime, timedelta
from backend.services.route_optimizer import RouteOptimizer

# Schedule pickup for 2 hours from now
pickup_time = datetime.now() + timedelta(hours=2)

result = RouteOptimizer.optimize_route(
    donor_lat=23.7599,
    donor_long=76.3421,
    receiver_lat=23.7703,
    receiver_long=76.3511,
    quantity=50,
    pickup_date=pickup_time
)

if result['success']:
    if result['route']['time_window_warning']:
        print(f"⚠️ Warning: {result['route']['time_window_warning']}")
    else:
        print(f"✅ Route is feasible within time window")
        print(f"Buffer: {result['route'].get('buffer_hours', 0)} hours")
```

### Example 2: API Request with Time Window
```bash
curl -X POST http://localhost:5000/api/routes/optimize \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_points": [[23.76, 76.34, 50, "9-12"]],
    "delivery_points": [[23.77, 76.35, 50, "13-16"]],
    "constraints": {
      "max_distance_km": 100,
      "max_time_hours": 4,
      "vehicle_capacity_kg": 500
    },
    "pickup_date": "2025-12-25T10:00:00"
  }'
```

### Example 3: Transaction with Scheduled Pickup
```python
# When creating a transaction
transaction = Transaction(
    donor_id=1,
    receiver_id=2,
    food_id=5,
    quantity=30,
    pickup_date=datetime(2025, 12, 25, 10, 0, 0)  # Specific scheduled time
)

# Route optimizer will automatically validate if delivery is feasible
# within the time window from now until pickup_date
```

## Backward Compatibility

- **No pickup_date provided**: Route optimization works as before without time constraints
- **Null pickup_date**: Treated same as not provided - no time validation
- **Existing transactions**: NULL pickup_date values are handled gracefully

## Benefits

1. **Realistic Planning**: Prevents scheduling impossible deliveries
2. **Urgency Awareness**: Routes consider time pressure from expiry/deadlines
3. **Better Coordination**: Donors and receivers get accurate feasibility feedback
4. **Automatic Validation**: System prevents accepting infeasible schedules

## Frontend Integration

To enable time window UI:

1. **Transaction Form**: Add datetime picker for `pickup_date`
2. **Route Optimizer Component**: Display time window warnings
3. **Match Acceptance**: Show feasibility status based on time window

Example React component update:
```tsx
{routeResult?.route?.time_window_warning && (
  <Alert variant="warning">
    <Clock className="h-4 w-4" />
    <AlertDescription>
      {routeResult.route.time_window_warning}
    </AlertDescription>
  </Alert>
)}
```

## Future Enhancements

Potential improvements:
1. **Traffic pattern awareness**: Adjust time estimates based on time of day
2. **Multi-day scheduling**: Support routes spanning multiple days
3. **Dynamic re-optimization**: Suggest better pickup times if current window is tight
4. **Calendar integration**: Block unavailable time slots
5. **Route clustering**: Group deliveries within same time window

## Testing

### Test Cases
1. ✅ Route with 4-hour advance pickup (should succeed with buffer)
2. ✅ Route with 30-min advance pickup (should warn about insufficient time)
3. ✅ Route with past pickup time (should reject)
4. ✅ Route with 10-day advance pickup (should warn about too far future)
5. ✅ Route without pickup_date (should work without time validation)

### Sample Test
```python
def test_time_window_validation():
    from datetime import datetime, timedelta
    from backend.services.route_optimizer import RouteOptimizer
    
    # Test insufficient time window
    soon_pickup = datetime.now() + timedelta(minutes=30)
    result = RouteOptimizer.optimize_route(
        donor_lat=23.76, donor_long=76.34,
        receiver_lat=23.80, receiver_long=76.38,  # ~5km distance
        quantity=50,
        pickup_date=soon_pickup
    )
    
    assert result['success'] == True
    assert result['route']['time_window_warning'] is not None
    assert 'Insufficient' in result['route']['time_window_warning']
```

## Configuration

No additional configuration required. Time window constraints are automatically applied when `pickup_date` is provided.

## Related Documentation
- [TRANSACTION_QUANTITY_PICKUP_DATE_ADDED.md](TRANSACTION_QUANTITY_PICKUP_DATE_ADDED.md) - Initial pickup_date field implementation
- [backend/services/route_optimizer.py](backend/services/route_optimizer.py) - Full route optimization logic
- [backend/models.py](backend/models.py) - Transaction model with pickup_date field
