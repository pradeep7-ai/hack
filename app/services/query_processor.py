import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.models import QueryRequest, QueryResponse, DocumentChunk, SearchResult

class QueryProcessor:
    """Main orchestrator for the RAG pipeline"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
        
        # Cache for processed documents
        self.document_cache = {}
    
    def process_query_request(self, request: QueryRequest) -> QueryResponse:
        """Main method to process a query request"""
        start_time = time.time()
        
        try:
            # Step 1: Process document (download, extract text, chunk)
            # [User Note] See logs for details on document processing steps
# print(f"Processing document: {request.documents}")
            chunks = self._process_document(request.documents)
            # [User Note] See logs for details on document processing steps
# print(f"Created {len(chunks)} chunks from document")
            
            # Step 2: Create embeddings and store in vector database
            # [User Note] See logs for details on document processing steps
# print(f"Creating embeddings for {len(chunks)} chunks")
            document_id = str(uuid.uuid4())
            embedding_ids = self.embedding_service.store_embeddings(chunks, document_id)
            # [User Note] See logs for details on document processing steps
# print(f"Stored {len(embedding_ids)} embeddings")
            
            # Step 3: Process each question
            answers = []
            metadata = {
                "document_id": document_id,
                "chunk_count": len(chunks),
                "embedding_ids": embedding_ids,
                "processing_details": []
            }
            
            for i, question in enumerate(request.questions):
                # [User Note] See logs for details on document processing steps
# print(f"Processing question {i+1}/{len(request.questions)}: {question}")
                
                # Step 4: Search for relevant chunks
                search_results = self.embedding_service.search_similar(
                    question, 
                    top_k=5,
                    filter_dict={"document_id": document_id}
                )
                # [User Note] See logs for details on document processing steps
# print(f"Found {len(search_results)} search results for question: {question[:50]}...")
                
                # Step 5: Generate answer using LLM
                llm_result = self.llm_service.generate_answer(question, search_results)
                
                # Step 6: Validate answer
                context_texts = [result.content for result in search_results]
                validation = self.llm_service.validate_answer(
                    llm_result["answer"], 
                    question, 
                    context_texts
                )
                
                # Store processing details
                processing_detail = {
                    "question_index": i,
                    "question": question,
                    "search_results_count": len(search_results),
                    "processing_time": llm_result.get("processing_time", 0),
                    "token_usage": llm_result.get("total_tokens", 0),
                    "validation_score": validation.get("score", 0),
                    "top_search_scores": [result.score for result in search_results[:3]]
                }
                metadata["processing_details"].append(processing_detail)
                
                answers.append(llm_result["answer"])
            
            # Calculate total processing time
            total_time = time.time() - start_time
            
            # Add summary metadata
            metadata.update({
                "total_processing_time": total_time,
                "total_questions": len(request.questions),
                "average_processing_time_per_question": total_time / len(request.questions),
                "document_url": request.documents,
                "processed_at": datetime.utcnow().isoformat()
            })
            
            return QueryResponse(
                answers=answers,
                metadata=metadata
            )
            
        except Exception as e:
            # [User Note] See logs for details on document processing steps
# print(f"Error in query processor: {str(e)}")
            # Return error response
            error_answers = [f"Error processing request: {str(e)}"] * len(request.questions)
            error_metadata = {
                "error": str(e),
                "processing_time": time.time() - start_time,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return QueryResponse(
                answers=error_answers,
                metadata=error_metadata
            )
    
    def _process_document(self, document_url: str) -> List[DocumentChunk]:
        """Process document and return chunks"""
        # Check cache first
        if document_url in self.document_cache:
            # [User Note] See logs for details on document processing steps
# print("Using cached document chunks")
            return self.document_cache[document_url]
        
        # Process document
        chunks = self.document_processor.process_document(document_url)
        
        # Cache the result
        self.document_cache[document_url] = chunks
        
        return chunks
    
    def process_single_question(self, question: str, document_url: str) -> Dict[str, Any]:
        """Process a single question for a document"""
        try:
            # Process document
            chunks = self._process_document(document_url)
            
            # Create embeddings if not already done
            document_id = str(uuid.uuid4())
            self.embedding_service.store_embeddings(chunks, document_id)
            
            # Search for relevant chunks
            search_results = self.embedding_service.search_similar(
                question, 
                top_k=5,
                filter_dict={"document_id": document_id}
            )
            
            # Generate answer
            llm_result = self.llm_service.generate_answer(question, search_results)
            
            # Extract structured query information
            structured_query = self.llm_service.extract_structured_query(question)
            
            # Generate explanation
            explanation = self.llm_service.generate_explanation(
                llm_result["answer"], 
                search_results
            )
            
            return {
                "question": question,
                "answer": llm_result["answer"],
                "search_results": [
                    {
                        "content": result.content[:200] + "...",
                        "score": result.score,
                        "source": result.source
                    }
                    for result in search_results[:3]
                ],
                "structured_query": structured_query,
                "explanation": explanation,
                "metadata": {
                    "processing_time": llm_result.get("processing_time", 0),
                    "token_usage": llm_result.get("total_tokens", 0),
                    "model": llm_result.get("model", ""),
                    "search_results_used": len(search_results)
                }
            }
            
        except Exception as e:
            return {
                "question": question,
                "answer": f"Error processing question: {str(e)}",
                "error": str(e)
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics and health information"""
        try:
            embedding_stats = self.embedding_service.get_embedding_stats()
            
            return {
                "system_status": "healthy",
                "embedding_service": embedding_stats,
                "document_cache_size": len(self.document_cache),
                "supported_formats": self.document_processor.supported_formats,
                "llm_model": self.llm_service.model,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "system_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear the document cache"""
        cache_size = len(self.document_cache)
        self.document_cache.clear()
        
        return {
            "message": "Cache cleared successfully",
            "cleared_items": cache_size,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def optimize_for_insurance_queries(self, question: str) -> str:
        """Optimize question for insurance-specific queries"""
        insurance_keywords = [
            "coverage", "policy", "premium", "claim", "benefit", "exclusion",
            "waiting period", "grace period", "deductible", "copay",
            "pre-existing", "maternity", "surgery", "hospitalization",
            "medication", "treatment", "diagnosis", "procedure"
        ]
        
        # Check if question contains insurance keywords
        question_lower = question.lower()
        has_insurance_keywords = any(keyword in question_lower for keyword in insurance_keywords)
        
        if has_insurance_keywords:
            # Add context for insurance queries
            enhanced_question = f"Insurance Policy Query: {question}"
            return enhanced_question
        
        return question 