#!/usr/bin/env python3
"""
Test script for deployed HackRx API
Replace YOUR_DEPLOYED_URL with your actual Render URL
"""

import requests
import json

# Replace with your actual deployed URL
BASE_URL = "https://your-app-name.onrender.com"
API_ENDPOINT = f"{BASE_URL}/hackrx/run"

# Authentication token (as specified in requirements)
AUTH_TOKEN = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"

# Test payload (from hackathon requirements)
test_payload = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}

def test_api():
    """Test the deployed API"""
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"Testing API at: {API_ENDPOINT}")
    print("Sending request...")
    
    try:
        response = requests.post(
            API_ENDPOINT,
            headers=headers,
            json=test_payload,
            timeout=60  # 60 second timeout
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Received {len(result.get('answers', []))} answers:")
            
            for i, answer in enumerate(result.get('answers', []), 1):
                print(f"\nQ{i}: {test_payload['questions'][i-1]}")
                print(f"A{i}: {answer}")
                
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT! Request took longer than 60 seconds")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_api()
