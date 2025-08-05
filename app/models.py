from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Pydantic Models for API
class QueryRequest(BaseModel):
    """Request model for document processing and query answering"""
    documents: str = Field(..., description="URL to the document (PDF/DOCX)")
    questions: List[str] = Field(..., description="List of questions to answer", min_items=1, max_items=20)

class QueryResponse(BaseModel):
    """Response model for query answers"""
    answers: List[str] = Field(..., description="List of answers corresponding to the questions")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the processing")

class DocumentChunk(BaseModel):
    """Model for document chunks"""
    content: str
    page_number: Optional[int] = None
    chunk_id: str
    metadata: Dict[str, Any] = {}

class SearchResult(BaseModel):
    """Model for search results"""
    content: str
    score: float
    source: str
    metadata: Dict[str, Any] = {}

class ProcessingStatus(BaseModel):
    """Model for processing status"""
    status: str
    message: str
    progress: Optional[float] = None
    timestamp: datetime