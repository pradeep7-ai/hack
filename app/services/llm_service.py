import os
import time
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

from app.models import SearchResult

load_dotenv()

class LLMService:
    """Service for handling LLM interactions with OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"  # Using GPT-3.5-turbo for much faster answers
        self.max_tokens = 500  # Reduced for faster responses
        self.temperature = 0.1  # Low temperature for consistent answers
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def create_context_prompt(self, query: str, search_results: List[SearchResult]) -> str:
        """Create a context-aware prompt for the LLM"""
        # Combine search results into context
        context_parts = []
        for i, result in enumerate(search_results[:3], 1):  # Use top 3 results
            context_parts.append(f"Relevant Text {i}:\n{result.content}\n")
        
        context = "\n".join(context_parts)
        
        prompt = f"""Answer this insurance question using the context below:

Context: {context}

Q: {query}
A:"""
        
        return prompt
    
    def generate_answer(self, query: str, search_results: List[SearchResult]) -> Dict[str, Any]:
        """Generate an answer for a single question using the LLM"""
        try:
            start_time = time.time()
            
            # Create the prompt
            prompt = self.create_context_prompt(query, search_results)
            
            # Estimate token usage
            input_tokens = self.count_tokens(prompt)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert insurance policy analyst with deep knowledge of health insurance, legal documents, and compliance requirements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract the answer
            answer = response.choices[0].message.content.strip()
            
            # Calculate processing time and token usage
            processing_time = time.time() - start_time
            output_tokens = self.count_tokens(answer)
            total_tokens = input_tokens + output_tokens
            
            return {
                "answer": answer,
                "processing_time": processing_time,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "model": self.model,
                "search_results_used": len(search_results)
            }
            
        except Exception as e:
            print(f"Error in generate_answer: {str(e)}")
            return {
                "answer": f"I encountered an error while processing your request: {str(e)}",
                "processing_time": time.time() - start_time if 'start_time' in locals() else 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "model": self.model,
                "search_results_used": len(search_results) if 'search_results' in locals() else 0,
                "error": str(e)
            }
            
    def generate_batch_answers(self, prompt: str, num_questions: int) -> Dict[str, Any]:
        """Generate answers for multiple questions in a single LLM call"""
        try:
            start_time = time.time()
            input_tokens = self.count_tokens(prompt)
            
            # Call OpenAI API with the batched prompt
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert insurance policy analyst. Answer each question based on its provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(4000, num_questions * 200),  # Allocate ~200 tokens per answer
                temperature=0.1  # Keep answers consistent
            )
            
            # Extract the full response
            full_response = response.choices[0].message.content.strip()
            output_tokens = self.count_tokens(full_response)
            
            # Parse the answers (they should be in format A1: ... A2: ... etc.)
            answers = [""] * num_questions
            for i in range(1, num_questions + 1):
                # Look for answer markers like "A1:", "A2:", etc.
                marker = f"A{i}:"
                next_marker = f"A{i+1}:" if i < num_questions else None
                
                start_idx = full_response.find(marker)
                if start_idx == -1:
                    answers[i-1] = "[Answer format error]"
                    continue
                    
                start_idx += len(marker)
                
                if next_marker:
                    end_idx = full_response.find(next_marker, start_idx)
                    if end_idx == -1:
                        end_idx = len(full_response)
                else:
                    end_idx = len(full_response)
                
                answer = full_response[start_idx:end_idx].strip()
                answers[i-1] = answer
            
            return {
                "answers": answers,
                "processing_time": time.time() - start_time,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "model": self.model
            }
            
        except Exception as e:
            print(f"Error in batch answer generation: {str(e)}")
            raise
            
        except Exception as e:
            print(f"Error in LLM service: {str(e)}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "processing_time": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "model": self.model,
                "error": str(e)
            }
    
    def extract_structured_query(self, user_query: str) -> Dict[str, Any]:
        """Extract structured information from user query"""
        try:
            prompt = f"""Analyze the following insurance policy question and extract structured information:

Question: {user_query}

Extract the following information in JSON format:
- query_type: The type of query (coverage, conditions, exclusions, benefits, etc.)
- key_terms: Important terms to search for
- specific_details: Any specific details mentioned (dates, amounts, procedures, etc.)
- intent: What the user is trying to find out

Return only valid JSON:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a query analysis expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                structured_data = json.loads(result)
                return structured_data
            except json.JSONDecodeError:
                # Fallback to basic extraction
                return {
                    "query_type": "general",
                    "key_terms": user_query.split(),
                    "specific_details": [],
                    "intent": "information_retrieval"
                }
                
        except Exception as e:
            return {
                "query_type": "general",
                "key_terms": user_query.split(),
                "specific_details": [],
                "intent": "information_retrieval",
                "error": str(e)
            }
    
    def validate_answer(self, answer: str, query: str, context: List[str]) -> Dict[str, Any]:
        """Validate the generated answer against the context"""
        try:
            prompt = f"""Validate if the following answer is accurate based on the provided context:

Query: {query}

Answer: {answer}

Context:
{chr(10).join(context)}

Rate the answer on a scale of 1-10 and provide feedback:
- Accuracy: How well does it match the context?
- Completeness: Does it cover all relevant information?
- Clarity: Is it clear and understandable?

Return JSON with: {{"score": number, "feedback": "text", "issues": ["list of issues"]}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a validation expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            try:
                validation = json.loads(result)
                return validation
            except json.JSONDecodeError:
                return {
                    "score": 7,
                    "feedback": "Unable to validate automatically",
                    "issues": ["JSON parsing error"]
                }
                
        except Exception as e:
            return {
                "score": 5,
                "feedback": f"Validation error: {str(e)}",
                "issues": ["Validation failed"]
            }
    
    def generate_explanation(self, answer: str, search_results: List[SearchResult]) -> str:
        """Generate an explanation of how the answer was derived"""
        try:
            sources = [f"- {result.source} (relevance: {result.score:.2f})" for result in search_results[:3]]
            sources_text = "\n".join(sources)
            
            prompt = f"""Explain how the following answer was derived from the search results:

Answer: {answer}

Sources used:
{sources_text}

Provide a brief explanation of the reasoning process:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an explanation expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Explanation generation failed: {str(e)}" 