from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any
import time

from app.models import QueryRequest, QueryResponse
from app.services.query_processor import QueryProcessor

# Security
security = HTTPBearer()

# Authentication middleware
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the Bearer token for API access"""
    expected_token = "a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return credentials.credentials

router = APIRouter()

# Initialize query processor
query_processor = QueryProcessor()

@router.post("/hackrx/run", response_model=QueryResponse)
async def run_hackrx_submission(request: QueryRequest):
    """
    Main endpoint for processing documents and answering questions.
    
    This endpoint implements the complete RAG pipeline:
    1. Downloads and processes the document (PDF/DOCX)
    2. Extracts text and creates chunks
    3. Generates embeddings and stores in vector database
    4. Searches for relevant chunks for each question
    5. Generates answers using LLM
    6. Returns structured JSON response
    """
    try:
        start_time = time.time()
        
        # Validate request
        if not request.documents:
            raise HTTPException(status_code=400, detail="Document URL is required")
        
        if not request.questions or len(request.questions) == 0:
            raise HTTPException(status_code=400, detail="At least one question is required")
        
        if len(request.questions) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 questions allowed per request")
        
        # Process the request
        print("=== REAL IMPLEMENTATION CALLED ===")
        response = query_processor.process_query_request(request)
        print("=== REAL IMPLEMENTATION COMPLETED ===")
        
        # Add request metadata
        if response.metadata:
            response.metadata["request_validation_time"] = time.time() - start_time
            response.metadata["questions_processed"] = len(request.questions)
        
        # Prepare and return the structured response for the API call
        # This response includes answers and relevant metadata for the client
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/hackrx/health")
async def health_check():
    """Health check endpoint for the HackRx system"""
    try:
        stats = query_processor.get_system_stats()
        return {
            "status": "healthy",
            "system_stats": stats,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@router.get("/hackrx/stats")
async def get_system_stats():
    """Get detailed system statistics"""
    try:
        stats = query_processor.get_system_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system stats: {str(e)}"
        )

@router.post("/hackrx/clear-cache")
async def clear_cache():
    """Clear the document cache"""
    try:
        result = query_processor.clear_cache()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )

@router.post("/hackrx/single-question")
async def process_single_question(question: str, document_url: str):
    """Process a single question for a document with detailed analysis"""
    try:
        if not question or not document_url:
            raise HTTPException(
                status_code=400, 
                detail="Both question and document_url are required"
            )
        
        result = query_processor.process_single_question(question, document_url)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )

@router.get("/hackrx/supported-formats")
async def get_supported_formats():
    """Get list of supported document formats"""
    return {
        "supported_formats": query_processor.document_processor.supported_formats,
        "description": "Document formats supported by the system"
    }

@router.get("/hackrx/embedding-stats")
async def get_embedding_stats():
    """Get embedding service statistics"""
    try:
        stats = query_processor.embedding_service.get_embedding_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get embedding stats: {str(e)}"
        )

# Additional utility endpoints for testing and development

@router.post("/hackrx/test-document-processing")
async def test_document_processing(document_url: str):
    """Test document processing without generating answers"""
    try:
        chunks = query_processor.document_processor.process_document(document_url)
        return {
            "status": "success",
            "chunks_created": len(chunks),
            "sample_chunk": chunks[0].content[:200] + "..." if chunks else None,
            "metadata": {
                "chunk_size": query_processor.document_processor.chunk_size,
                "chunk_overlap": query_processor.document_processor.chunk_overlap
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing test failed: {str(e)}"
        )

@router.post("/hackrx/test-embeddings")
async def test_embeddings(text: str):
    """Test embedding generation for a text"""
    try:
        embedding = query_processor.embedding_service.create_single_embedding(text)
        token_count = query_processor.embedding_service.count_tokens(text)
        
        return {
            "status": "success",
            "embedding_dimension": len(embedding),
            "token_count": token_count,
            "text_length": len(text),
            "model": query_processor.embedding_service.model_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding test failed: {str(e)}"
        )

@router.get("/hackrx/version")
async def get_version():
    """Get system version information"""
    return {
        "version": "1.0.0",
        "name": "HackRx 6.0 - LLM-Powered Query-Retrieval System",
        "description": "An intelligent system for processing documents and answering queries in insurance, legal, HR, and compliance domains",
        "features": [
            "Multi-format document processing (PDF, DOCX)",
            "Semantic search using Pinecone",
            "LLM-powered answer generation",
            "Explainable decision rationale",
            "Token optimization",
            "Real-time processing"
        ],
        "tech_stack": [
            "FastAPI",
            "Pinecone",
            "OpenAI GPT-4",
            "Sentence Transformers",
            "PyMuPDF",
            "PostgreSQL"
        ]
    } 