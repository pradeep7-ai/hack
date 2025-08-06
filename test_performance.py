import requests
import json
import time
import os
from datetime import datetime

# Configuration
USE_LOCAL = True  # Set to False to test against production
LOCAL_BASE_URL = "http://localhost:8000"
REMOTE_BASE_URL = "https://raghack.onrender.com"
BASE_URL = LOCAL_BASE_URL if USE_LOCAL else REMOTE_BASE_URL
API_ENDPOINT = f"{BASE_URL}/hackrx/run"
AUTH_TOKEN = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"

if USE_LOCAL:
    print("⚠️  TESTING AGAINST LOCAL SERVER")
    print("   Make sure to run: uvicorn main:app --reload\n")
else:
    print("⚠️  TESTING AGAINST PRODUCTION SERVER\n")

# Performance diagnostic test

# Test with different question counts
test_cases = [
    {
        "name": "Single Question Test",
        "questions": ["What is the grace period for premium payment?"]
    },
    {
        "name": "Three Questions Test", 
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?"
        ]
    },
    {
        "name": "Hackathon 10-Question Test",
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
]

def test_performance(test_case):
    # Use a local PDF for testing if running locally
    document_url = (
        "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    )
    
    request_data = {
        "documents": document_url,
        "questions": test_case["questions"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    print(f"\n🔍 {test_case['name']}")
    print(f"Questions: {len(test_case['questions'])}")
    print("-" * 40)
    
    try:
        # Warm-up request (don't time this)
        if len(test_case['questions']) > 3:  # Only for larger test cases
            print("🔥 Warming up...")
            try:
                warm_up_data = request_data.copy()
                warm_up_data['questions'] = warm_up_data['questions'][:1]  # Just one question for warm-up
                requests.post(API_ENDPOINT, headers=headers, json=warm_up_data, timeout=30)
            except Exception as e:
                print(f"  Warm-up warning: {str(e)}")
        
        # Actual timed request
        print(f"🚀 Sending {len(test_case['questions'])} questions...")
        start_time = time.time()
        response = requests.post(API_ENDPOINT, headers=headers, json=request_data, timeout=60)
        response_time = time.time() - start_time
        
        print(f"✅ Response received in {response_time:.2f}s")
        print(f"📊 Performance: {response_time:.2f}s total, {response_time/len(test_case['questions']):.2f}s per question")
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get('answers', [])
            print(f"Answers received: {len(answers)}")
            
            # Print first 3 answers in full, summarize the rest
            max_answers_to_show = 3
            for i, answer in enumerate(answers):
                if i < max_answers_to_show:
                    print(f"\nQ{i+1}: {test_case['questions'][i]}")
                    print(f"A{i+1}: {answer[:300]}{'...' if len(answer) > 300 else ''}")
                
            if len(answers) > max_answers_to_show:
                print(f"\n... and {len(answers) - max_answers_to_show} more answers ...")
        else:
            print(f"❌ ERROR: {response.text[:100]}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT (>60s)")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def main():
    print("🚀 PERFORMANCE DIAGNOSTIC TEST")
    print("=" * 50)
    print(f"Testing against: {'LOCAL' if USE_LOCAL else 'REMOTE'} server at {BASE_URL}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    for test_case in test_cases:
        test_performance(test_case)
    
    print("\n" + "=" * 50)
    print("📊 ANALYSIS:")
    if USE_LOCAL:
        print("Local server testing tips:")
        print("1. Run with: uvicorn main:app --reload --workers 1")
        print("2. Check CPU/RAM usage during testing")
        print("3. Monitor API logs for timing breakdown")
    print("\nPerformance targets:")
    print("- Single question: <5s")
    print("- 3 questions: <10s")
    print("- 10 questions: <30s (hackathon requirement)")
    print("\nCommon bottlenecks:",
          "1. Document download/processing time" if USE_LOCAL else "1. Network latency to remote server",
          "2. OpenAI API rate limits",
          "3. Pinecone query performance",
          "4. LLM response time (especially with large context)", sep="\n- ")

if __name__ == "__main__":
    main()
