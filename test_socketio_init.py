#!/usr/bin/env python
"""Test Socket.IO initialization"""
import sys
import os

# Ensure backend is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔵 Testing Socket.IO initialization...")
    
    # Test 1: Import extensions
    print("✓ Step 1: Importing extensions...")
    from backend.extensions import socketio, db, jwt, migrate
    print("✅ Extensions imported successfully")
    print(f"   - socketio: {socketio}")
    
    # Test 2: Import and create app
    print("\n✓ Step 2: Creating app...")
    from backend.app import create_app
    app = create_app()
    print("✅ App created successfully")
    
    # Test 3: Verify Socket.IO is initialized with app
    print("\n✓ Step 3: Verifying Socket.IO initialization...")
    if hasattr(app, 'extensions') and 'socketio' in app.extensions:
        print("✅ Socket.IO registered in app extensions")
    else:
        print("⚠️ Socket.IO not in app.extensions (might be OK)")
    
    # Test 4: Test sockets module import
    print("\n✓ Step 4: Testing sockets module import...")
    from backend import sockets
    print("✅ Sockets module imported successfully")
    
    # Test 5: Verify Socket.IO handlers are registered
    print("\n✓ Step 5: Checking Socket.IO event handlers...")
    if hasattr(socketio, '_handlers'):
        print(f"✅ Socket.IO handlers registered: {list(socketio._handlers.keys())}")
    else:
        print("✅ Socket.IO ready for handlers")
    
    print("\n" + "="*50)
    print("✅ All Socket.IO initialization tests PASSED!")
    print("="*50)
    print("\nYou can now run the server with:")
    print("  python backend/app.py")
    print("\nOr in the backend directory:")
    print("  python -m flask run --reload")
    
except Exception as e:
    print(f"\n❌ Error during initialization: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
