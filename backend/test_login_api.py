#!/usr/bin/env python
"""Test the login endpoint to see what error is being returned"""

import requests
import json

url = "http://127.0.0.1:8001/auth/login"

# Test with valid credentials
payload = {
    "email": "farmer@test.com",
    "password": "password123"
}

print(f"📤 Testing login endpoint: {url}")
print(f"📋 Payload: {json.dumps(payload)}")

try:
    response = requests.post(url, json=payload, timeout=5)
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📥 Response Headers: {dict(response.headers)}")
    
    try:
        data = response.json()
        print(f"📥 Response Body:\n{json.dumps(data, indent=2)}")
    except:
        print(f"📥 Response Body (raw):\n{response.text}")
    
    if response.status_code == 200:
        print("\n✅ Login successful!")
    else:
        print(f"\n❌ Error: Status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
