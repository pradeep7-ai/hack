import requests
import json
import time

# EXACT hackathon specifications test
print("🔍 HACKATHON COMPLIANCE VERIFICATION")
print("=" * 60)

# Test Configuration
BASE_URL = "https://raghack.onrender.com"
API_ENDPOINT = f"{BASE_URL}/hackrx/run"
AUTH_TOKEN = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"

# EXACT request format from hackathon documentation
hackathon_request = {
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

# EXACT headers from hackathon documentation
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {AUTH_TOKEN}"
}

def verify_compliance():
    print(f"🎯 Testing API Endpoint: {API_ENDPOINT}")
    print(f"📝 Request Format Verification:")
    print(f"   ✓ Content-Type: {headers['Content-Type']}")
    print(f"   ✓ Accept: {headers['Accept']}")
    print(f"   ✓ Authorization: Bearer <token>")
    print(f"   ✓ Document URL: {hackathon_request['documents'][:50]}...")
    print(f"   ✓ Questions Count: {len(hackathon_request['questions'])}")
    print("-" * 60)
    
    try:
        # Send EXACT request as hackathon judges would
        start_time = time.time()
        response = requests.post(
            API_ENDPOINT, 
            headers=headers, 
            json=hackathon_request, 
            timeout=30
        )
        response_time = time.time() - start_time
        
        print(f"📊 Response Analysis:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {response_time:.2f}s")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ JSON Response: Valid")
                
                # Verify EXACT response format
                print(f"\n🔍 Response Format Verification:")
                
                # Check if 'answers' key exists
                if 'answers' in result:
                    print(f"   ✅ 'answers' key: Present")
                    
                    # Check if answers is a list
                    if isinstance(result['answers'], list):
                        print(f"   ✅ 'answers' type: List")
                        print(f"   ✅ Answers count: {len(result['answers'])}")
                        print(f"   ✅ Expected count: {len(hackathon_request['questions'])}")
                        
                        # Verify each answer is a string
                        all_strings = all(isinstance(answer, str) for answer in result['answers'])
                        print(f"   ✅ All answers are strings: {all_strings}")
                        
                        # Check response structure matches exactly
                        expected_keys = {'answers'}
                        actual_keys = set(result.keys())
                        
                        print(f"\n📋 Response Structure:")
                        print(f"   Expected keys: {expected_keys}")
                        print(f"   Actual keys: {actual_keys}")
                        print(f"   Extra keys: {actual_keys - expected_keys}")
                        
                        # Show sample answers
                        print(f"\n📝 Sample Answers (First 3):")
                        for i, answer in enumerate(result['answers'][:3], 1):
                            question = hackathon_request['questions'][i-1]
                            print(f"   Q{i}: {question[:60]}...")
                            print(f"   A{i}: {answer[:80]}...")
                            print()
                        
                        # Final compliance check
                        print(f"🎯 COMPLIANCE SUMMARY:")
                        compliance_checks = [
                            ("Endpoint /hackrx/run", True),
                            ("HTTPS enabled", API_ENDPOINT.startswith('https')),
                            ("Status 200", response.status_code == 200),
                            ("Response time < 30s", response_time < 30),
                            ("JSON response", True),
                            ("'answers' key present", 'answers' in result),
                            ("Answers is list", isinstance(result.get('answers'), list)),
                            ("Correct answer count", len(result.get('answers', [])) == len(hackathon_request['questions'])),
                            ("All answers are strings", all_strings),
                            ("Bearer auth working", True)
                        ]
                        
                        all_passed = True
                        for check, passed in compliance_checks:
                            status = "✅" if passed else "❌"
                            print(f"   {status} {check}")
                            if not passed:
                                all_passed = False
                        
                        print(f"\n🏆 FINAL RESULT:")
                        if all_passed:
                            print("   🎉 100% HACKATHON COMPLIANT!")
                            print("   🚀 Ready for successful submission!")
                        else:
                            print("   ⚠️  Some compliance issues found")
                            
                    else:
                        print(f"   ❌ 'answers' type: {type(result['answers'])}")
                else:
                    print(f"   ❌ 'answers' key: Missing")
                    print(f"   Available keys: {list(result.keys())}")
                    
            except json.JSONDecodeError:
                print(f"   ❌ JSON Response: Invalid")
                print(f"   Raw response: {response.text[:200]}...")
                
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout: Request took longer than 30 seconds")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request Error: {str(e)}")
    except Exception as e:
        print(f"   ❌ Unexpected Error: {str(e)}")

if __name__ == "__main__":
    verify_compliance()
