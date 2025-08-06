import requests
import json

# Test with the EXACT hackathon test case
BASE_URL = "https://raghack.onrender.com"
API_ENDPOINT = f"{BASE_URL}/hackrx/run"

# Authentication token
AUTH_TOKEN = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"

# EXACT hackathon test payload (from their documentation)
hackathon_payload = {
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

def test_exact_format():
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("🎯 Testing EXACT Hackathon Format")
    print("=" * 60)
    print(f"Endpoint: {API_ENDPOINT}")
    print(f"Questions: {len(hackathon_payload['questions'])}")
    print("=" * 60)
    
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=hackathon_payload, timeout=120)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Response Keys: {list(result.keys())}")
            print(f"Number of Answers: {len(result.get('answers', []))}")
            
            # Check exact format
            if 'answers' in result and isinstance(result['answers'], list):
                print("✅ Correct format: {'answers': [...]}")
                
                # Show first few answers
                for i, answer in enumerate(result['answers'][:3], 1):
                    print(f"\nQ{i}: {hackathon_payload['questions'][i-1][:50]}...")
                    print(f"A{i}: {answer[:100]}...")
                
                print(f"\n... and {len(result['answers']) - 3} more answers")
                
                # Verify JSON structure matches expected
                expected_format = {"answers": ["string1", "string2", "..."]}
                print(f"\n🎯 Format Check:")
                print(f"Expected: {expected_format}")
                print(f"Your API: {{'answers': ['{len(result['answers'])} answers']}}")
                print("✅ FORMAT MATCHES PERFECTLY!")
                
            else:
                print("❌ Wrong format! Expected: {'answers': [...]}")
                
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_exact_format()
