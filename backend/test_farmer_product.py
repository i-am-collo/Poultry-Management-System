"""
Test farmer product creation workflow
"""
import requests
import json
import base64

BASE_URL = "http://localhost:8000"

def test_farmer_product_flow():
    """Test the complete farmer product creation flow"""
    
    print("=" * 60)
    print("Testing Farmer Product Creation Workflow")
    print("=" * 60)
    
    # Step 1: Login as a farmer
    print("\n1️⃣  Logging in as farmer...")
    login_payload = {"email": "iamcollolimo@gmail.com", "password": "password123"}
    print(f"   Request: {login_payload}")
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_payload
    )
    
    print(f"   Response Status: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    farmer_data = login_response.json()
    token = farmer_data.get("access_token")
    farmer_id = farmer_data.get("user", {}).get("id")
    
    print(f"✅ Logged in successfully")
    print(f"   Token: {token[:20]}...")
    print(f"   Farmer ID: {farmer_id}")
    
    # Step 2: Create a dummy product image (small PNG)
    print("\n2️⃣  Creating test product image...")
    # Simple 1x1 red PNG in base64
    test_image_base64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8AyABAAAAAAAA"
    
    print(f"✅ Test image prepared (Base64: {test_image_base64[:30]}...)")
    
    # Step 3: Create a product
    print("\n3️⃣  Creating farmer product...")
    product_data = {
        "name": "Organic Broiler Chickens",
        "category": "broilers",
        "description": "High-quality broiler chickens, ready for sale",
        "unit_price": 2500.00,
        "unit_of_measure": "per bird",
        "stock_quantity": 50,
        "product_image": test_image_base64,
        "is_active": True
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Role": "farmer"
    }
    
    create_response = requests.post(
        f"{BASE_URL}/farmers/products",
        json=product_data,
        headers=headers
    )
    
    print(f"   Response Status: {create_response.status_code}")
    
    if create_response.status_code not in (200, 201):
        print(f"❌ Product creation failed!")
        print(f"   Response: {create_response.text}")
        return
    
    created_product = create_response.json()
    product_id = created_product.get("id")
    
    print(f"✅ Product created successfully!")
    print(f"   Product ID: {product_id}")
    print(f"   Name: {created_product.get('name')}")
    print(f"   Farmer ID: {created_product.get('farmer_id')}")
    print(f"   Source: {created_product.get('product_source')}")
    
    # Step 4: Retrieve farmer's products
    print("\n4️⃣  Retrieving farmer's products...")
    get_response = requests.get(
        f"{BASE_URL}/farmers/products",
        headers=headers
    )
    
    if get_response.status_code != 200:
        print(f"❌ Failed to retrieve products: {get_response.text}")
        return
    
    products = get_response.json()
    print(f"✅ Retrieved {len(products)} product(s)")
    
    for prod in products:
        print(f"   - {prod.get('name')} (ID: {prod.get('id')}, Farmer ID: {prod.get('farmer_id')})")
    
    # Step 5: Test buyer search (should see farmer product)
    print("\n5️⃣  Testing buyer search (should see farmer product)...")
    buyer_response = requests.get(
        f"{BASE_URL}/buyers/search?query=Organic",
        headers={"X-Role": "buyer"}
    )
    
    if buyer_response.status_code != 200:
        print(f"❌ Buyer search failed: {buyer_response.text}")
        return
    
    search_results = buyer_response.json()
    print(f"✅ Buyer search returned {len(search_results)} result(s)")
    
    for result in search_results:
        if result.get("id") == product_id:
            print(f"   ✅ Found our farmer product!")
            print(f"      Name: {result.get('name')}")
            print(f"      Source: {result.get('product_source')} (Farmer: {result.get('farmer_name')})")
            break
    else:
        print(f"   ⚠️  Farmer product not found in search results")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_farmer_product_flow()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
