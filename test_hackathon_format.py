import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change this if your server is running elsewhere
ENDPOINT = f"{BASE_URL}/hackrx/run"
AUTH_TOKEN = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"

def send_hackathon_request():
    """Send a request in the exact hackathon format and display results"""
    # Prepare the request data
    request_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?",
            "What is the No Claim Discount (NCD) offered in this policy?",
            "Is there a benefit for preventive health check-ups?",
            "How does the policy define a 'Hospital'?",
            "What is the extent of coverage for AYUSH treatments?",
            "Are there any sub-limits on room rent and ICU charges for Plan A?"
        ]
    }
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    print("🚀 Sending hackathon format request...")
    print("-" * 50)
    print(f"POST {ENDPOINT}")
    print("Headers:")
    for key, value in headers.items():
        print(f"{key}: {value}")
    print("\nBody:")
    print(json.dumps(request_data, indent=4))
    print("\n" + "=" * 50 + "\n")
    
    try:
        # Send the request
        start_time = time.time()
        response = requests.post(
            ENDPOINT,
            headers=headers,
            json=request_data,
            timeout=60  # 60 seconds timeout
        )
        response_time = time.time() - start_time
        
        # Process the response
        print(f"✅ Response received in {response_time:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Print the response in the exact format
            print("\nResponse:")
            print(json.dumps({"answers": result['answers']}, indent=4))
            
            # Print individual Q&A for better readability
            print("\n" + "=" * 50)
            print("📋 Question & Answer Pairs:")
            print("=" * 50)
            for i, (question, answer) in enumerate(zip(request_data['questions'], result['answers']), 1):
                print(f"\nQ{i}: {question}")
                print(f"A{i}: {answer}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (60 seconds)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    print("🏁 HACKATHON FORMAT TEST")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    send_hackathon_request()
