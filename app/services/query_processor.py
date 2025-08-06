import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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
        """Process a query request with multiple questions using batched LLM calls"""
        try:
            start_time = time.time()
            
            # Step 1: Process document if URL is provided
            document_id = None
            if request.documents:
                try:
                    chunks = self.document_processor.process_document(request.documents)
                    document_id = str(uuid.uuid4())
                    self.embedding_service.store_embeddings(chunks, document_id)
                except Exception as doc_err:
                    return QueryResponse(
                        answers=[f"Error processing document: {str(doc_err)}"] * len(request.questions)
                    )
            
            # Step 2: Process questions in batch
            try:
                # Process all questions in a single batch
                search_results = []
                for question in request.questions:
                    results = self.embedding_service.search_similar(
                        question,
                        top_k=1,
                        filter_dict={"document_id": document_id} if document_id else None
                    )
                    search_results.append(results[0] if results else None)
                
                # Create a single prompt for all questions
                batch_prompt = self._create_batch_prompt(request.questions, search_results)
                
                # Get batch answers
                llm_response = self.llm_service.generate_batch_answers(batch_prompt, len(request.questions))
                
                # Parse the answers
                answers = llm_response.get("answers", [f"Error: Could not generate answer"] * len(request.questions))
                
                # Ensure we have the right number of answers
                if len(answers) != len(request.questions):
                    answers = [f"Error: Mismatch in number of answers"] * len(request.questions)
                
                return QueryResponse(answers=answers)
                
            except Exception as llm_err:
                print(f"Batch processing failed, falling back to individual processing: {str(llm_err)}")
                return self._process_individually(request, document_id, start_time)
                
        except Exception as e:
            return QueryResponse(
                answers=[f"Error processing request: {str(e)}" for _ in request.questions]
            )
            
    def _create_batch_prompt(self, questions: List[str], search_results: List[Any]) -> str:
        """Create a single prompt with all questions and their contexts"""
        prompt_parts = [
            "You are an expert insurance policy analyst. Answer the following questions based on the provided context for each.",
            "For each question, use only the context provided immediately before it.",
            "If the answer is not in the context, say 'Not specified in the document'.",
            "Format your answers exactly as: A1: [answer]\nA2: [answer] and so on.\n\n"
        ]
        
        for i, (question, result) in enumerate(zip(questions, search_results), 1):
            context = result.content if result else "No relevant context found."
            prompt_parts.extend([
                f"--- CONTEXT FOR QUESTION {i} ---\n",
                f"{context}\n\n",
                f"Q{i}: {question}\n",
                f"A{i}:"  # Leave space for the answer
            ])
            
            # Add separation between Q&A pairs
            if i < len(questions):
                prompt_parts.append("\n\n")
        
        return "".join(prompt_parts)
    
    def _process_individually(self, request: QueryRequest, document_id: str, start_time: float) -> QueryResponse:
        """Fallback method to process questions individually"""
        try:
            answers = [""] * len(request.questions)
            
            for idx, question in enumerate(request.questions):
                try:
                    search_results = self.embedding_service.search_similar(
                        question, 
                        top_k=1,
                        filter_dict={"document_id": document_id} if document_id else None
                    )
                    
                    # Process with LLM
                    context = search_results[0].content if search_results else "No relevant context found."
                    prompt = f"Question: {question}\n\nContext:\n{context}\n\nAnswer:"
                    
                    llm_result = self.llm_service.generate_answer(prompt, search_results)
                    answers[idx] = llm_result.get("answer", "Error generating answer")
                    
                except Exception as qe:
                    answers[idx] = f"Error processing question: {str(qe)}"
            
            return QueryResponse(answers=answers)
            
        except Exception as e:
            error_answers = [f"Error processing request: {str(e)}"] * len(request.questions) if hasattr(request, 'questions') else ["Internal server error"]
            return QueryResponse(answers=error_answers)

    
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