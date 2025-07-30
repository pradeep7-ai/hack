from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base

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

# SQLAlchemy Models
Base = declarative_base()

class Document(Base):
    """Database model for documents"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)
    filename = Column(String(255))
    file_type = Column(String(50))
    processed_at = Column(DateTime, default=datetime.utcnow)
    chunk_count = Column(Integer, default=0)
    embedding_status = Column(String(50), default="pending")
    document_metadata = Column(JSON)

class Query(Base):
    """Database model for queries"""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    document_id = Column(Integer)
    processing_time = Column(Float)
    token_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    query_metadata = Column(JSON)

class DocumentChunkDB(Base):
    """Database model for document chunks"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_id = Column(String(255), unique=True, index=True)
    page_number = Column(Integer)
    embedding_id = Column(String(255))
    chunk_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow) 