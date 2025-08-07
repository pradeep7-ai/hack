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
        """Process a query request with multiple questions using parallel processing"""
        try:
            start_time = time.time()
            
            # Step 1: Process document if URL is provided (single document for all questions)
            document_id = None
            if request.documents:
                try:
                    print(f"Processing document: {request.documents}")
                    chunks = self.document_processor.process_document(request.documents)
                    document_id = str(uuid.uuid4())
                    self.embedding_service.store_embeddings(chunks, document_id)
                    print(f"Document processed. Generated {len(chunks)} chunks.")
                except Exception as doc_err:
                    error_msg = f"Error processing document: {str(doc_err)}"
                    print(error_msg)
                    return QueryResponse(answers=[error_msg] * len(request.questions))
            
            # Step 2: Process questions in parallel batches
            try:
                print(f"Processing {len(request.questions)} questions in parallel...")
                
                # Process questions in batches of 3 with 2 parallel workers
                batch_size = 3
                max_workers = 2
                answers = [""] * len(request.questions)  # Pre-allocate answer list
                
                def process_question_batch(batch_indices, questions_batch):
                    """Process a batch of questions and update answers in place"""
                    try:
                        # Get search results for this batch
                        batch_results = []
                        for question in questions_batch:
                            results = self.embedding_service.search_similar(
                                question,
                                top_k=3,  # Reduced from 5 to 3 for speed
                                filter_dict={"document_id": document_id} if document_id else None
                            )
                            batch_results.append(results)
                        
                        # Process batch with LLM
                        batch_answers = self._process_question_batch(
                            questions_batch, 
                            batch_results, 
                            document_id
                        )
                        
                        # Update answers in the pre-allocated list
                        for i, idx in enumerate(batch_indices):
                            if i < len(batch_answers):
                                answers[idx] = batch_answers[i]
                        
                        return True, None
                    except Exception as e:
                        error_msg = str(e)
                        print(f"Error in batch processing: {error_msg}")
                        for i, idx in enumerate(batch_indices):
                            answers[idx] = f"[Error: {error_msg[:100]}]"
                        return False, error_msg
                
                # Process batches in parallel
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = []
                    
                    # Create batches
                    for i in range(0, len(request.questions), batch_size):
                        batch_indices = list(range(i, min(i + batch_size, len(request.questions))))
                        questions_batch = [request.questions[idx] for idx in batch_indices]
                        
                        # Submit batch for processing
                        future = executor.submit(process_question_batch, batch_indices, questions_batch)
                        futures.append(future)
                    
                    # Wait for all batches to complete
                    for future in futures:
                        future.result()  # Will raise exception if any batch fails
                
                print(f"Successfully processed all {len(answers)} answers.")
                return QueryResponse(answers=answers)
                
            except Exception as e:
                error_msg = f"Error in parallel processing: {str(e)}"
                print(error_msg)
                return QueryResponse(answers=[error_msg] * len(request.questions))
                
        except Exception as e:
            error_msg = f"Error processing query request: {str(e)}"
            print(error_msg)
            return QueryResponse(answers=[error_msg] * len(request.questions) if hasattr(request, 'questions') else [error_msg])
            
    def _create_batch_prompt(self, questions: List[str], search_results: List[List[SearchResult]]) -> str:
        """Create an optimized prompt for faster processing"""
        prompt = [
            "You are an insurance expert. Answer concisely based on the context.\n\n",
            "GUIDELINES:\n",
            "1. Be direct and to the point\n",
            "2. Include key details like numbers and conditions\n",
            "3. If context is unclear, say so\n",
            "4. If answer isn't in context, say 'Not specified'\n",
            "5. Format as: A1: [answer]\nA2: [answer]\n\n"
        ]
        
        for i, (question, results) in enumerate(zip(questions, search_results), 1):
            prompt.append(f"Q{i}: {question}\n")
            
            if results:
                prompt.append("Context:\n")
                # Use only top 2 most relevant contexts for speed
                for j, result in enumerate(results[:2], 1):
                    prompt.append(f"- {result.content[:300]}...\n")
            else:
                prompt.append("No context.\n")
            
            prompt.append(f"A{i}:")
            
            if i < len(questions):
                prompt.append("\n\n")
        
        return "".join(prompt)
    
    def _process_question_batch(self, questions: List[str], search_results_list: List[List[SearchResult]], document_id: str) -> List[str]:
        """Process a batch of questions with their search results"""
        try:
            # Create a comprehensive prompt for this batch
            batch_prompt = self._create_batch_prompt(questions, search_results_list)
            
            # Get batch answers from LLM
            llm_response = self.llm_service.generate_batch_answers(
                batch_prompt,
                len(questions)
            )
            
            # Extract and validate answers
            answers = []
            for i, question in enumerate(questions):
                try:
                    answer = llm_response.get("answers", [])[i] if i < len(llm_response.get("answers", [])) else ""
                    
                    # Validate answer quality
                    if not answer or len(answer.strip()) < 5:  # Very short answer
                        answer = self._get_fallback_answer(question, search_results_list[i])
                    
                    answers.append(answer)
                    
                except Exception as e:
                    print(f"Error processing answer for question {i+1}: {str(e)}")
                    answers.append("I couldn't generate a complete answer for this question.")
            
            return answers
            
        except Exception as e:
            print(f"Error in _process_question_batch: {str(e)}")
            return ["Error processing questions"] * len(questions)
    
    def _get_fallback_answer(self, question: str, search_results: List[SearchResult]) -> str:
        """Get a fallback answer when batch processing fails"""
        try:
            if not search_results:
                return "The policy does not contain information to answer this question."
                
            # Try to find the answer in the most relevant chunk
            context = "\n\n".join([f"Context {i+1}:\n{result.content}" 
                                   for i, result in enumerate(search_results[:3])])
            
            prompt = f"""Answer the question based ONLY on the following context. If the answer isn't in the context, say "The policy does not specify this information."

Question: {question}

Context:
{context}

Answer in one or two clear sentences:"""
            
            response = self.llm_service.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error in _get_fallback_answer: {str(e)}")
            return "I couldn't find a complete answer in the policy document."
    
    def _process_individually(self, request: QueryRequest, document_id: str, start_time: float) -> QueryResponse:
        """Fallback method to process questions individually with enhanced error handling"""
        try:
            answers = []
            
            for idx, question in enumerate(request.questions):
                try:
                    print(f"Processing question {idx+1} individually: {question[:50]}...")
                    
                    # Get more context for individual processing
                    search_results = self.embedding_service.search_similar(
                        question, 
                        top_k=5,  # Get more context for individual processing
                        filter_dict={"document_id": document_id} if document_id else None
                    )
                    
                    if not search_results:
                        answers.append("No relevant information found in the document.")
                        continue
                    
                    # Process with LLM using the enhanced prompt
                    llm_result = self.llm_service.generate_answer(question, search_results)
                    answer = llm_result.get("answer", "")
                    
                    # Validate answer
                    if not answer or len(answer.strip()) < 5:
                        answer = self._get_fallback_answer(question, search_results)
                    
                    answers.append(answer)
                    
                except Exception as qe:
                    error_msg = f"Error processing question: {str(qe)}"
                    print(error_msg)
                    answers.append("I encountered an error while processing this question.")
            
            return QueryResponse(answers=answers)
            
        except Exception as e:
            error_msg = f"Error in _process_individually: {str(e)}"
            print(error_msg)
            error_answers = ["I'm having trouble processing this request. Please try again later."] * len(request.questions)
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