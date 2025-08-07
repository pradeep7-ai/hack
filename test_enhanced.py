import requests
import json
import time
import concurrent.futures
from typing import Dict, List, Any, Tuple
from datetime import datetime, timezone

def process_batch(batch_num: int, questions: List[str], url: str, api_key: str) -> Tuple[int, List[Dict], float]:
    """Process a single batch of questions"""
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prepare the request data according to the API's expected format
    data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09:11:24Z&se=2027-07-05T09:11:00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT/jUHNO7HzQ=",
        "questions": questions
    }
    
    batch_start = time.time()
    results = []
    
    try:
        print(f"\nSending request to {url} with {len(questions)} questions...")
        print(f"Headers: {headers}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            response.raise_for_status()
            
        response_data = response.json()
        print(f"Response data: {json.dumps(response_data, indent=2)}")
        
        batch_answers = response_data.get('answers', [])
        
        for i, (question, answer) in enumerate(zip(questions, batch_answers), 1):
            results.append({
                "question_number": (batch_num - 1) * len(questions) + i,
                "question": question,
                "answer": answer,
                "status": "success"
            })
            
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Error in batch {batch_num}: {error_msg}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
            
        for i, question in enumerate(questions, 1):
            results.append({
                "question_number": (batch_num - 1) * len(questions) + i,
                "question": question,
                "answer": f"[Error: {error_msg}]",
                "status": "error"
            })
    
    return batch_num, results, time.time() - batch_start

def test_enhanced_api() -> List[Dict]:
    """Test the API with optimized settings and return results in JSON format."""
    # API Configuration
    API_URL = "http://localhost:8000/hackrx/run"
    API_KEY = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"
    
    # Print configuration for debugging
    print("\n" + "="*80)
    print("TEST CONFIGURATION")
    print("="*80)
    print(f"API URL: {API_URL}")
    print(f"Document: Using provided policy PDF")
    print(f"Number of questions: 10")
    print("="*80 + "\n")
    
    # Sample questions that require detailed answers
    questions = [
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
    
    # Configuration - process questions in batches of 3 with 2 parallel workers
    batch_size = 3
    max_workers = 2
    
    all_results = []
    processed_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit batches to thread pool
        futures = []
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            future = executor.submit(process_batch, len(futures) + 1, batch, API_URL, API_KEY)
            futures.append(future)
            
            # Print progress
            processed_count += len(batch)
            print(f"\nSubmitted batch {len(futures)} with {len(batch)} questions "
                  f"(Total processed: {min(processed_count, len(questions))}/{len(questions)})")
        
        # Process completed batches as they finish
        for future in concurrent.futures.as_completed(futures):
            try:
                batch_num, batch_results, batch_time = future.result()
                
                # Add batch results
                all_results.extend(batch_results)
                
                print(f"✓ Batch {batch_num} completed in {batch_time:.2f} seconds")
                
            except Exception as e:
                print(f"✗ Error processing batch: {str(e)}")
                batch_num = futures.index(future) + 1
                for q in questions[(batch_num-1)*batch_size : batch_num*batch_size]:
                    all_results.append({
                        "question_number": batch_num,
                        "question": q,
                        "answer": f"[Error: {str(e)[:100]}]",
                        "status": "error"
                    })
    
    return all_results

def format_answers_for_hackathon(results: List[Dict]) -> Dict:
    """Format answers in the exact structure required by the hackathon"""
    # Extract just the answers in order
    answers = []
    for result in sorted(results, key=lambda x: x["question_number"]):
        answers.append(result["answer"])
    
    return {"answers": answers}

if __name__ == "__main__":
    start_time = time.time()
    results = test_enhanced_api()
    
    # Format output exactly as required by hackathon
    final_output = format_answers_for_hackathon(results)
    
    # Print the final JSON output with no extra whitespace
    print("\n" + "="*80)
    print("HACKATHON FORMATTED OUTPUT")
    print("="*80)
    print(json.dumps(final_output, indent=4))
    
    # Print timing info separately (not part of the hackathon output)
    print("\nTest completed successfully!")
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")
