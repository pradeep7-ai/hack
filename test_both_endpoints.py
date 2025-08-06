import requests
import json

# Test both endpoints locally
BASE_URL = "https://raghack.onrender.com"
#BASE_URL = "http://localhost:8000"
ENDPOINTS = [
    f"{BASE_URL}/hackrx/run",           # New hackathon endpoint
    f"{BASE_URL}/api/v1/hackrx/run"     # Original endpoint
]

# Authentication token
AUTH_TOKEN = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"

# Test payload
test_payload = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment?"
    ]
}

def test_endpoint(endpoint_url, name):
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"\n🔍 Testing {name}: {endpoint_url}")
    
    try:
        response = requests.post(endpoint_url, headers=headers, json=test_payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Answer: {result.get('answers', ['No answers'])[0][:100]}...")
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def main():
    print("🚀 Testing Both Endpoints Locally")
    print("=" * 50)
    
    test_endpoint(ENDPOINTS[0], "Hackathon Endpoint")
    test_endpoint(ENDPOINTS[1], "Original Endpoint")
    
    print("\n" + "=" * 50)
    print("📝 Summary:")
    print("Both endpoints should return Status Code 200")
    print("This confirms your API works for hackathon submission!")

if __name__ == "__main__":
    main()
