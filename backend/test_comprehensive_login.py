import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = 'http://127.0.0.1:8001'
TEST_EMAIL = 'farmer@test.com'
TEST_PASSWORD = 'password123'

print("=" * 70)
print("COMPREHENSIVE LOGIN TEST")
print("=" * 70)
print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Test 1: Test login endpoint
print("TEST 1: Direct Login")
print("-" * 70)
try:
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    print(f"📤 Sending POST /auth/login")
    print(f"   Payload: {json.dumps(payload)}")
    
    response = requests.post(
        f'{API_BASE_URL}/auth/login',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"📥 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"   - Access Token: {data['access_token'][:50]}...")
        print(f"   - Refresh Token: {data['refresh_token'][:50]}...")
        print(f"   - User: {data['user']['email']} ({data['user']['role']})")
        print(f"   - Token Type: {data['token_type']}")
    else:
        print(f"❌ Login failed with status {response.status_code}")
        print(f"   Response: {response.json()}")

except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n")

# Test 2: Test with JWT token (simulating authenticated request)
print("TEST 2: Authenticated Request with JWT Token")
print("-" * 70)
try:
    # First login to get token
    login_response = requests.post(
        f'{API_BASE_URL}/auth/login',
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        print(f"✅ Got access token: {token[:50]}...")
        
        # Try to use token for authenticated request
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print(f"📤 Testing health endpoint with token...")
        health_response = requests.get(
            f'{API_BASE_URL}/health',
            headers=headers
        )
        
        if health_response.status_code == 200:
            print(f"✅ Health endpoint accessible with token")
            print(f"   Response: {health_response.json()}")
        else:
            print(f"❌ Health endpoint returned {health_response.status_code}")
    else:
        print(f"❌ Could not get token: {login_response.json()}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n")

# Test 3: Test CORS headers
print("TEST 3: CORS Headers Check")
print("-" * 70)
try:
    response = requests.options(
        f'{API_BASE_URL}/auth/login',
        headers={
            'Origin': 'http://127.0.0.1:3000',
            'Access-Control-Request-Method': 'POST',
        }
    )
    
    print(f"📤 Sent OPTIONS request to /auth/login")
    print(f"   Origin: http://127.0.0.1:3000")
    print(f"📥 Response Headers:")
    
    cors_headers = {
        'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
        'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
    }
    
    for header, value in cors_headers.items():
        print(f"   - {header}: {value if value else '(not set)'}")
    
    if cors_headers['Access-Control-Allow-Origin']:
        print("✅ CORS is configured")
    else:
        print("⚠️  CORS headers not found in OPTIONS response")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n")

# Test 4: Test wrong password
print("TEST 4: Login with Wrong Password")
print("-" * 70)
try:
    response = requests.post(
        f'{API_BASE_URL}/auth/login',
        json={
            "email": TEST_EMAIL,
            "password": "wrongpassword123"
        }
    )
    
    print(f"📤 Sending login with wrong password")
    print(f"📥 Status Code: {response.status_code}")
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected with 400")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ Unexpected status code {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n")

# Test 5: Test non-existent email
print("TEST 5: Login with Non-existent Email")
print("-" * 70)
try:
    response = requests.post(
        f'{API_BASE_URL}/auth/login',
        json={
            "email": "nonexistent@test.com",
            "password": "password123"
        }
    )
    
    print(f"📤 Sending login with non-existent email")
    print(f"📥 Status Code: {response.status_code}")
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected with 400")
        print(f"   Error: {response.json()['detail']}")
    else:
        print(f"❌ Unexpected status code {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)
