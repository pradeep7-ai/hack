import os
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from app.models import DocumentChunk, SearchResult
from app.services.vector_store import VectorStore

load_dotenv()

class EmbeddingService:
    """Service for handling document embeddings and vector search"""
    
    def __init__(self):
        # Initialize the unified vector store
        self.vector_store = VectorStore(use_pinecone=True, use_faiss=False)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return self.vector_store.count_tokens(text)
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        return self.vector_store.create_embeddings(texts)
    
    def create_single_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        return self.vector_store.create_single_embedding(text)
    
    def store_embeddings(self, chunks: List[DocumentChunk], document_id: str) -> List[str]:
        """Store embeddings in vector store"""
        return self.vector_store.store_embeddings(chunks, document_id)
    
    def search_similar(self, query: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[SearchResult]:
        """Search for similar documents using vector similarity"""
        return self.vector_store.search_similar(query, top_k, filter_dict)
    
    def delete_document_embeddings(self, document_id: str) -> bool:
        """Delete all embeddings for a specific document"""
        return self.vector_store.delete_document_embeddings(document_id)
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding index"""
        return self.vector_store.get_stats()
    
    def batch_process_chunks(self, chunks: List[DocumentChunk], batch_size: int = 16) -> List[List[float]]:
        """Process chunks in batches to avoid memory issues"""
        all_embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [chunk.content for chunk in batch]
            batch_embeddings = self.create_embeddings(texts)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings 