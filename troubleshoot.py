#!/usr/bin/env python3
"""
Quick troubleshooting script for 403 Unauthorized errors
Run this to verify your setup and get a valid token
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_api_status():
    """Check if API is running"""
    print_section("1. Checking API Status")
    try:
        response = requests.get(f"{BASE_URL}/api/mongodb/status", timeout=5)
        print(f"✅ API Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API on http://localhost:5000")
        print("   Make sure Flask server is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def login_user():
    """Login user and get token"""
    print_section("2. Logging In User")
    
    login_credentials = {
        "email": "donor@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_credentials,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User logged in successfully!")
            print(f"   Email: {login_credentials['email']}")
            print(f"   User ID: {data.get('user_id')}")
            print(f"\n📋 Token (save this):\n{data.get('access_token')}\n")
            return data.get('access_token')
        elif response.status_code == 401:
            print(f"❌ Invalid credentials (401 Unauthorized)")
            print("   Email or password is incorrect")
            print(json.dumps(response.json(), indent=2))
            return None
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_with_token(token):
    """Test authentication with token"""
    print_section("3. Testing Authentication")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Token: {token[:50]}...")
    print(f"\nTesting: GET /api/mongodb/test-auth\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/mongodb/test-auth",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Authentication successful! (200 OK)")
            print(json.dumps(response.json(), indent=2))
            return True
        elif response.status_code == 401:
            print(f"❌ Invalid token (401 Unauthorized)")
            print(json.dumps(response.json(), indent=2))
            return False
        elif response.status_code == 403:
            print(f"❌ Token rejected (403 Forbidden)")
            print(json.dumps(response.json(), indent=2))
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_transactions_endpoint(token):
    """Test actual transactions endpoint"""
    print_section("4. Testing Transactions Endpoint")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Testing: GET /api/mongodb/transactions\n")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/mongodb/transactions",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Transactions endpoint working! (200 OK)")
            print(json.dumps(response.json(), indent=2))
            return True
        elif response.status_code == 503:
            print(f"⚠️  MongoDB not available (503)")
            print("   This is OK - API still works with PostgreSQL")
            print(json.dumps(response.json(), indent=2))
            return True
        elif response.status_code == 403:
            print(f"❌ Authorization failed (403)")
            print(json.dumps(response.json(), indent=2))
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  FRNS API Troubleshooting Tool")
    print("="*60)
    
    # Step 1: Check API
    if not check_api_status():
        print("\n❌ Please start the Flask server first:")
        print("   cd backend")
        print("   python app.py")
        sys.exit(1)
    
    # Step 2: Login user
    token = login_user()
    if not token:
        print("\n⚠️  Could not login user. Check credentials and try again...")
    
    # Step 3: Test auth
    if token and test_with_token(token):
        # Step 4: Test transactions
        test_transactions_endpoint(token)
    
    print_section("Summary")
    if token:
        print("✅ Setup complete! Your token is:\n")
        print(token)
        print("\n📋 How to use in Postman:")
        print("1. Click 'Authorization' tab")
        print("2. Select 'Bearer Token' from dropdown")
        print("3. Paste the token above")
        print("4. Send request")
    else:
        print("❌ Setup failed. Check the errors above.")

if __name__ == "__main__":
    main()
