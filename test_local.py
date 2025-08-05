import requests
import json

# Local API endpoint
BASE_URL = "https://raghack.onrender.com/"
API_ENDPOINT = f"{BASE_URL}/api/v1/hackrx/run"

# Authentication token
AUTH_TOKEN = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"

# Test payload
test_payload = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?",
        "Does this policy cover maternity expenses?"
    ]
}

def test_local_api():
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"Testing LOCAL API at: {API_ENDPOINT}")
    
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=test_payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LOCAL TEST SUCCESS!")
            for i, answer in enumerate(result.get('answers', []), 1):
                print(f"\nQ{i}: {test_payload['questions'][i-1]}")
                print(f"A{i}: {answer}")
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_local_api()