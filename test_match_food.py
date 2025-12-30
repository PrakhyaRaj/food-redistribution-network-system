import inspect
import sys
sys.path.insert(0, '.')

from backend.routes.food_routes import match_food

source = inspect.getsource(match_food)
lines = source.split('\n')

# Check if AnalyticsService is in the function
analytics_count = sum(1 for line in lines if 'AnalyticsService' in line)
match_count = sum(1 for line in lines if '[MATCH]' in line)
sync_count = sum(1 for line in lines if 'SYNC ANALYTICS' in line)

print(f"✅ match_food function loaded")
print(f"   - Lines with 'AnalyticsService': {analytics_count}")
print(f"   - Lines with '[MATCH]': {match_count}")
print(f"   - Lines with 'SYNC ANALYTICS': {sync_count}")

if analytics_count > 0 and sync_count > 0:
    print(f"✅ Analytics sync code IS present in match_food!")
    # Print the relevant lines
    print(f"\nRelevant lines from match_food:")
    for i, line in enumerate(lines):
        if 'SYNC ANALYTICS' in line or 'AnalyticsService' in line or '[MATCH]' in line:
            print(f"  Line {i}: {line.strip()}")
else:
    print(f"❌ Analytics sync code NOT found in match_food!")
    print(f"\nShowing last 10 lines of match_food:")
    for line in lines[-10:]:
        print(f"  {line}")
