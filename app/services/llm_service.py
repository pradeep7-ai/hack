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
        self.model = "gpt-4-1106-preview"  # Fastest GPT-4 model
        self.max_tokens = 600  # Reduced for faster responses
        self.temperature = 0.2  # Slightly higher for better quality
        self.max_retries = 1  # Single attempt for speed
        self.timeout = 20  # Reduced timeout for faster failure
        self.batch_size = 3  # Number of questions to process in parallel
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
        
    def create_context_prompt(self, query: str, search_results: List[SearchResult]) -> str:
        """Create a streamlined prompt for faster processing"""
        # Use only top 2 most relevant contexts for speed
        context = "\n".join([f"- {result.content[:500]}..." 
                            for i, result in enumerate(search_results[:2])])
        
        prompt = f"""Answer concisely based on the context. Be direct and include key details.

CONTEXT:
{context}

QUESTION: {query}

ANSWER: """
        
        return prompt
    
    def _create_batch_prompt(self, questions: List[str], search_results: List[List[SearchResult]]) -> str:
        """Create an optimized prompt for batch processing"""
        # Build context from all search results
        contexts = []
        for i, (question, results) in enumerate(zip(questions, search_results), 1):
            context = "\n".join(f"- {r.content[:300]}..." for r in results[:2])  # Shorter context
            contexts.append(f"QUESTION {i}: {question}\nCONTEXT:\n{context}")
        
        questions_text = "\n\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
        
        prompt = f"""You are an insurance expert. Answer each question concisely based on its context.
Keep answers under 100 words. Use bullet points when listing items.

For each question, provide an answer in the format:
A1: [Answer to question 1]
A2: [Answer to question 2]
...

QUESTIONS:
{questions_text}

CONTEXTS:
""" + "\n\n".join(contexts) + "\n\nANSWERS:\n"
        
        # Truncate if too long
        if len(prompt) > 6000:  # Leave room for answers
            prompt = prompt[:6000] + "\n[Context truncated for length]\n\nANSWERS:\n"
            
        return prompt
    
    def _process_question_batch(self, questions: List[str], search_results: List[List[SearchResult]], document_id: str = None) -> List[str]:
        """Process a batch of questions with their search results"""
        if not questions or not search_results or len(questions) != len(search_results):
            return ["Error: Invalid input"] * len(questions) if questions else []
            
        try:
            # Create a single prompt for all questions to reduce API calls
            prompt = self._create_batch_prompt(questions, search_results)
            
            # Get batch answer from LLM with shorter timeout
            start_time = time.time()
            answer_text = self.generate_answer(prompt, max_tokens=800)
            processing_time = time.time() - start_time
            
            print(f"LLM processing time: {processing_time:.2f}s for {len(questions)} questions")
            
            # Parse the response to extract individual answers
            answers = self._parse_batch_answers(answer_text, len(questions))
            
            # If parsing failed, fall back to individual processing
            if len(answers) != len(questions) or any("[Error" in a for a in answers):
                print("Batch processing failed, falling back to individual processing")
                return self._process_individually(questions, search_results, document_id)
                
            return answers
            
        except Exception as e:
            error_msg = f"Error in batch processing: {str(e)[:200]}"
            print(error_msg)
            
            # Fall back to individual processing on error
            try:
                return self._process_individually(questions, search_results, document_id)
            except Exception as fallback_error:
                print(f"Fallback processing also failed: {str(fallback_error)[:200]}")
                return [f"Error: {str(e)[:100]}"] * len(questions)
    
    def _parse_batch_answers(self, answer_text: str, num_questions: int) -> List[str]:
        """Parse the batch answer text into individual answers"""
        answers = [""] * num_questions
        for i in range(1, num_questions + 1):
            # Look for answer markers like "A1:", "A2:", etc.
            marker = f"A{i}:"
            next_marker = f"A{i+1}:" if i < num_questions else None
            
            start_idx = answer_text.find(marker)
            if start_idx == -1:
                answers[i-1] = "[Answer format error]"
                continue
            
            start_idx += len(marker)
            
            if next_marker:
                end_idx = answer_text.find(next_marker, start_idx)
                if end_idx == -1:
                    end_idx = len(answer_text)
            else:
                end_idx = len(answer_text)
            
            answer = answer_text[start_idx:end_idx].strip()
            answers[i-1] = answer if answer else "[No answer provided]"
        
        return answers
    
    def _process_individually(self, questions: List[str], search_results: List[List[SearchResult]], document_id: str = None) -> List[str]:
        """Process questions individually"""
        answers = []
        for question, result in zip(questions, search_results):
            answer = self.generate_answer(question, search_results=[result])
            answers.append(answer)
        
        return answers
    
    def generate_answer(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate an answer using the LLM with optimized parameters for speed"""
        try:
            # Truncate very long prompts to save on processing time
            if len(prompt) > 6000:  # Roughly 1500 tokens
                prompt = prompt[:3000] + "\n[Content truncated for efficiency]\n" + prompt[-3000:]
                
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides concise and accurate answers. Be brief but complete in your responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(max_tokens, 500),  # Reduced for faster responses
                temperature=0.2,  # Lower temperature for more focused, consistent answers
                top_p=0.95,  # Slightly higher than default for some creativity
                frequency_penalty=0.1,  # Slightly reduce repetition
                presence_penalty=0.0,  # No presence penalty for faster response
                n=1,
                stop=None,
                timeout=15,  # Reduced timeout for faster failure
                request_timeout=20  # Total request timeout
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating answer: {str(e)[:200]}")
            return f"[Error: {str(e)[:100]}]"  # Truncate long errors
    
    def generate_batch_answers(self, prompt: str, num_questions: int) -> Dict[str, Any]:
        """Generate detailed answers for multiple questions with improved batching and error handling"""
        start_time = time.time()
        last_error = None
        
        # Enhanced system message with detailed instructions
        system_message = """You are a senior insurance policy analyst with deep expertise in health insurance policies.

INSTRUCTIONS:
1. For each question, provide a comprehensive answer based ONLY on the provided context.
2. Be precise with numbers, dates, and policy-specific terms.
3. Include all relevant details, limitations, and conditions from the context.
4. If the context is unclear or contradictory, state that explicitly.
5. If the answer isn't in the context, say "The policy does not specify this information."
6. Format your answers as:
   A1: [detailed answer]
   A2: [detailed answer]
   ... and so on.

IMPORTANT:
- Be thorough but concise.
- Use bullet points or numbered lists when appropriate.
- Include specific policy terms and conditions when relevant.
- If a question has multiple parts, address each part clearly."""
        
        # Estimate token usage
        input_tokens = self.count_tokens(prompt) + self.count_tokens(system_message)
        
        # Retry logic for batch API calls
        for attempt in range(self.max_retries):
            try:
                # Call OpenAI API with optimized parameters for detailed responses
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=min(8000, num_questions * 600),  # More tokens for detailed answers
                    temperature=0.1,  # Lower for more focused and consistent answers
                    top_p=0.95,
                    frequency_penalty=0.1,
                    presence_penalty=0.1,
                    timeout=self.timeout * 3  # Increased timeout for detailed responses
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
                    answers[i-1] = answer if answer else "[No answer provided]"
                
                # Calculate processing time and token usage
                processing_time = time.time() - start_time
                total_tokens = input_tokens + output_tokens
                
                return {
                    "answers": answers,
                    "processing_time": processing_time,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "model": self.model
                }
            
            except Exception as e:
                print(f"Error in batch answer generation (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                last_error = e
                if attempt == self.max_retries - 1:  # Last attempt
                    print(f"All {self.max_retries} attempts failed. Last error: {str(e)}")
                    return {
                        "answers": [f"Error: {str(e)}"] * num_questions,
                        "processing_time": time.time() - start_time,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "model": self.model,
                        "error": str(e)
                    }
                # Exponential backoff before retry
                time.sleep(2 ** attempt)
        
        # If we get here, all retries failed
        return {
            "answers": [f"Error: Failed to generate answers after {self.max_retries} attempts. {str(last_error)}"] * num_questions,
            "processing_time": time.time() - start_time,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "model": self.model,
            "error": str(last_error) if last_error else "Unknown error"
        }
    
    def extract_structured_query(self, user_query: str) -> Dict[str, Any]:
        """Extract structured information from user query with improved parsing"""
        try:
            prompt = f"""Analyze the following insurance policy question and extract structured information:

Question: {user_query}

Extract the following information in JSON format:
- query_type: The type of query (coverage, conditions, exclusions, benefits, claims, premiums, etc.)
- key_terms: List of important insurance-related terms to search for
- specific_details: Any specific details mentioned (dates, amounts, procedures, etc.)
- intent: What the user is trying to find out
- priority: High/Medium/Low based on potential impact

Return only valid JSON, no other text. If unsure about any field, use null."""

            response = self.client.chat.completions.create(
                model="gpt-4-1106-preview",  # Always use GPT-4 for better JSON parsing
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a query analysis expert. Analyze insurance policy questions and extract structured information. "
                                  "Return ONLY valid JSON with the specified fields. Do not include any other text in your response."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},  # Ensure valid JSON output
                max_tokens=500,
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