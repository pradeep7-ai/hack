#!/usr/bin/env python3
"""
Demo script for HackRx 6.0 - LLM-Powered Query-Retrieval System

This script demonstrates the complete RAG pipeline with sample data.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
AUTH_TOKEN = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"

# Sample test data
SAMPLE_DOCUMENT_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

SAMPLE_QUESTIONS = [
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

def make_request(endpoint: str, method: str = "GET", data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make HTTP request to the API"""
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": str(e)}

def test_health_check():
    """Test system health"""
    print("🔍 Testing system health...")
    result = make_request("/hackrx/health")
    print(f"Health Status: {result.get('status', 'unknown')}")
    return result

def test_version():
    """Test version endpoint"""
    print("\n📋 Testing version endpoint...")
    result = make_request("/hackrx/version")
    print(f"Version: {result.get('version', 'unknown')}")
    print(f"Name: {result.get('name', 'unknown')}")
    return result

def test_supported_formats():
    """Test supported formats"""
    print("\n📄 Testing supported formats...")
    result = make_request("/hackrx/supported-formats")
    formats = result.get('supported_formats', [])
    print(f"Supported formats: {', '.join(formats)}")
    return result

def test_system_stats():
    """Test system statistics"""
    print("\n📊 Testing system statistics...")
    result = make_request("/hackrx/stats")
    print(f"System Status: {result.get('system_status', 'unknown')}")
    return result

def test_document_processing():
    """Test document processing"""
    print("\n📝 Testing document processing...")
    result = make_request("/hackrx/test-document-processing", method="POST", params={"document_url": SAMPLE_DOCUMENT_URL})
    if "chunks_created" in result:
        print(f"Chunks created: {result['chunks_created']}")
        print(f"Sample chunk: {result.get('sample_chunk', 'N/A')}")
    return result

def test_embeddings():
    """Test embedding generation"""
    print("\n🧠 Testing embedding generation...")
    test_text = "This is a test text for embedding generation."
    result = make_request("/hackrx/test-embeddings", method="POST", params={"text": test_text})
    if "embedding_dimension" in result:
        print(f"Embedding dimension: {result['embedding_dimension']}")
        print(f"Token count: {result['token_count']}")
    return result

def test_single_question():
    """Test single question processing"""
    print("\n❓ Testing single question processing...")
    question = "What is the grace period for premium payment?"
    result = make_request("/hackrx/single-question", method="POST", params={
        "question": question,
        "document_url": SAMPLE_DOCUMENT_URL
    })
    
    if "answer" in result:
        print(f"Question: {result['question']}")
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Processing time: {result.get('metadata', {}).get('processing_time', 0):.2f}s")
    return result

def test_main_endpoint():
    """Test the main /hackrx/run endpoint"""
    print("\n🚀 Testing main endpoint with sample questions...")
    
    # Use first 3 questions for demo
    demo_questions = SAMPLE_QUESTIONS[:3]
    
    request_data = {
        "documents": SAMPLE_DOCUMENT_URL,
        "questions": demo_questions
    }
    
    start_time = time.time()
    result = make_request("/hackrx/run", method="POST", data=request_data)
    end_time = time.time()
    
    if "answers" in result:
        print(f"✅ Successfully processed {len(result['answers'])} questions")
        print(f"⏱️  Total processing time: {end_time - start_time:.2f}s")
        
        for i, (question, answer) in enumerate(zip(demo_questions, result['answers'])):
            print(f"\nQ{i+1}: {question}")
            print(f"A{i+1}: {answer[:200]}...")
        
        # Show metadata
        metadata = result.get('metadata', {})
        if metadata:
            print(f"\n📈 Processing Details:")
            print(f"   - Total processing time: {metadata.get('total_processing_time', 0):.2f}s")
            print(f"   - Average time per question: {metadata.get('average_processing_time_per_question', 0):.2f}s")
            print(f"   - Chunks processed: {metadata.get('chunk_count', 0)}")
    
    return result

def test_error_handling():
    """Test error handling"""
    print("\n⚠️  Testing error handling...")
    
    # Test with invalid URL
    request_data = {
        "documents": "https://invalid-url-that-does-not-exist.com/document.pdf",
        "questions": ["What is covered?"]
    }
    
    result = make_request("/hackrx/run", method="POST", data=request_data)
    if "error" in result or any("error" in answer.lower() for answer in result.get('answers', [])):
        print("✅ Error handling working correctly")
    else:
        print("❌ Error handling may need improvement")
    
    return result

def run_comprehensive_demo():
    """Run comprehensive demo of all features"""
    print("🎯 HackRx 6.0 - Comprehensive Demo")
    print("=" * 50)
    
    # Test basic endpoints
    test_health_check()
    test_version()
    test_supported_formats()
    test_system_stats()
    
    # Test core functionality
    test_document_processing()
    test_embeddings()
    test_single_question()
    
    # Test main endpoint
    test_main_endpoint()
    
    # Test error handling
    test_error_handling()
    
    print("\n🎉 Demo completed!")
    print("\n📚 Next steps:")
    print("1. Set up your environment variables (see env.example)")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application: uvicorn main:app --reload")
    print("4. Access the API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    run_comprehensive_demo() 