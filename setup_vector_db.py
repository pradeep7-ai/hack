#!/usr/bin/env python3
"""
Setup script for vector database
This script helps you set up and test the vector database functionality
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.services.vector_store import VectorStore
from app.services.document_processor import DocumentProcessor
from app.models import DocumentChunk

def test_vector_store():
    """Test the vector store functionality"""
    print("🔧 Testing Vector Store Setup...")
    
    try:
        # Initialize vector store
        print("📦 Initializing Vector Store...")
        vector_store = VectorStore(use_pinecone=True, use_faiss=True)
        
        # Get stats
        stats = vector_store.get_stats()
        print("📊 Vector Store Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Test embedding creation
        print("\n🧠 Testing Embedding Creation...")
        test_texts = [
            "This is a test document about health insurance.",
            "The policy covers maternity expenses and pre-existing conditions.",
            "Grace period is thirty days for premium payment."
        ]
        
        embeddings = vector_store.create_embeddings(test_texts)
        print(f"✅ Created {len(embeddings)} embeddings")
        print(f"📏 Embedding dimension: {len(embeddings[0])}")
        
        # Test storing embeddings
        print("\n💾 Testing Embedding Storage...")
        chunks = []
        for i, text in enumerate(test_texts):
            chunk = DocumentChunk(
                content=text,
                chunk_id=f"test_chunk_{i}",
                metadata={"test": True, "index": i}
            )
            chunks.append(chunk)
        
        embedding_ids = vector_store.store_embeddings(chunks, "test_document")
        print(f"✅ Stored {len(embedding_ids)} embeddings")
        
        # Test search
        print("\n🔍 Testing Vector Search...")
        search_results = vector_store.search_similar("health insurance policy", top_k=3)
        print(f"✅ Found {len(search_results)} results")
        
        for i, result in enumerate(search_results):
            print(f"  Result {i+1}: Score={result.score:.3f}")
            print(f"    Content: {result.content[:100]}...")
        
        print("\n🎉 Vector Store Setup Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Vector Store Setup Failed: {e}")
        return False

def test_document_processing():
    """Test document processing functionality"""
    print("\n📄 Testing Document Processing...")
    
    try:
        processor = DocumentProcessor()
        
        # Test with sample text
        sample_text = """
        National Parivar Mediclaim Plus Policy provides comprehensive health coverage.
        The policy includes maternity benefits and covers pre-existing diseases after a waiting period.
        Grace period of thirty days is provided for premium payment.
        """
        
        chunks = processor.chunk_text(sample_text, chunk_size=200, overlap=50)
        print(f"✅ Created {len(chunks)} chunks from sample text")
        
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: {len(chunk.content)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Document Processing Failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Vector Database Setup")
    print("=" * 50)
    
    # Test document processing
    doc_success = test_document_processing()
    
    # Test vector store
    vector_success = test_vector_store()
    
    print("\n" + "=" * 50)
    print("📋 Setup Summary:")
    print(f"  Document Processing: {'✅ PASS' if doc_success else '❌ FAIL'}")
    print(f"  Vector Store: {'✅ PASS' if vector_success else '❌ FAIL'}")
    
    if doc_success and vector_success:
        print("\n🎉 All tests passed! Your vector database is ready.")
        print("\n📝 Next steps:")
        print("  1. Run your FastAPI application")
        print("  2. Upload documents through the API")
        print("  3. Test search functionality")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("  1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("  2. Check your .env file for Pinecone configuration (optional)")
        print("  3. Ensure you have write permissions in the current directory")

if __name__ == "__main__":
    main() 