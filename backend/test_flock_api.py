#!/usr/bin/env python
"""Test the flock creation API endpoint"""

import requests
import json
from app.core.security import create_access_token
from app.db.database import SessionLocal
from app.models.user import User

# Get a test farmer user
db = SessionLocal()
farmer = db.query(User).filter(User.role == 'farmer').first()

if not farmer:
    print("❌ No farmer user found in database. Creating one...")
    from app.core.security import hash_password
    farmer = User(
        name="Test Farmer",
        email="testfarmer@test.com",
        phone="254712345678",
        hashed_password=hash_password("password123"),
        role="farmer"
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    print(f"✅ Created farmer: {farmer.email}")

# Create a JWT token for the farmer
token = create_access_token(farmer.email, farmer.role)

print(f"✅ Using farmer: {farmer.email} (ID: {farmer.id})")
print(f"✅ Token: {token[:20]}...")

# Test the flock creation endpoint
url = "http://127.0.0.1:8001/farmers/register-flock"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "bird_type": "broiler",
    "breed": "Ross 308",
    "quantity": 100,
    "age_weeks": 2,
    "health_status": "healthy",
    "daily_feed_kg": 5.0,
    "notes": "Test flock creation"
}

print(f"\n📤 Sending POST request to {url}")
print(f"📋 Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=5)
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📥 Response Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"📥 Response Body:\n{json.dumps(response_data, indent=2)}")
    except:
        print(f"📥 Response Body (raw):\n{response.text}")
    
    if response.status_code == 201:
        print("\n✅ Flock created successfully!")
    else:
        print(f"\n❌ Error: Status {response.status_code}")
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except requests.exceptions.Timeout as e:
    print(f"❌ Timeout error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
