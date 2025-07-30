import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from main import app

client = TestClient(app)

class TestHackRxAPI:
    """Test cases for HackRx API endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "HackRx 6.0" in data["message"]
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_version_endpoint(self):
        """Test version endpoint"""
        response = client.get("/api/v1/hackrx/version")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"
        assert "FastAPI" in data["tech_stack"]
    
    def test_supported_formats(self):
        """Test supported formats endpoint"""
        response = client.get("/api/v1/hackrx/supported-formats")
        assert response.status_code == 200
        data = response.json()
        assert ".pdf" in data["supported_formats"]
        assert ".docx" in data["supported_formats"]
    
    def test_hackrx_run_missing_auth(self):
        """Test that authentication is required"""
        request_data = {
            "documents": "https://example.com/test.pdf",
            "questions": ["What is covered?"]
        }
        response = client.post("/api/v1/hackrx/run", json=request_data)
        assert response.status_code == 401
    
    def test_hackrx_run_with_auth(self):
        """Test the main run endpoint with authentication"""
        headers = {
            "Authorization": "Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"
        }
        request_data = {
            "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            "questions": [
                "What is the grace period for premium payment?",
                "Does this policy cover knee surgery?"
            ]
        }
        
        with patch('app.services.query_processor.QueryProcessor.process_query_request') as mock_process:
            mock_response = Mock()
            mock_response.answers = [
                "A grace period of thirty days is provided for premium payment.",
                "Yes, the policy covers knee surgery under specific conditions."
            ]
            mock_response.metadata = {"test": "metadata"}
            mock_process.return_value = mock_response
            
            response = client.post("/api/v1/hackrx/run", json=request_data, headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert "answers" in data
            assert len(data["answers"]) == 2
    
    def test_hackrx_run_invalid_request(self):
        """Test invalid request handling"""
        headers = {
            "Authorization": "Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"
        }
        
        # Test missing documents
        request_data = {"questions": ["What is covered?"]}
        response = client.post("/api/v1/hackrx/run", json=request_data, headers=headers)
        assert response.status_code == 400
        
        # Test missing questions
        request_data = {"documents": "https://example.com/test.pdf"}
        response = client.post("/api/v1/hackrx/run", json=request_data, headers=headers)
        assert response.status_code == 400
        
        # Test too many questions
        request_data = {
            "documents": "https://example.com/test.pdf",
            "questions": [f"Question {i}" for i in range(25)]
        }
        response = client.post("/api/v1/hackrx/run", json=request_data, headers=headers)
        assert response.status_code == 400
    
    def test_single_question_endpoint(self):
        """Test single question processing endpoint"""
        headers = {
            "Authorization": "Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"
        }
        
        with patch('app.services.query_processor.QueryProcessor.process_single_question') as mock_process:
            mock_result = {
                "question": "What is covered?",
                "answer": "Test answer",
                "search_results": [],
                "metadata": {}
            }
            mock_process.return_value = mock_result
            
            response = client.post(
                "/api/v1/hackrx/single-question",
                params={"question": "What is covered?", "document_url": "https://example.com/test.pdf"},
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["question"] == "What is covered?"
    
    def test_clear_cache_endpoint(self):
        """Test cache clearing endpoint"""
        headers = {
            "Authorization": "Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"
        }
        
        with patch('app.services.query_processor.QueryProcessor.clear_cache') as mock_clear:
            mock_result = {"message": "Cache cleared", "cleared_items": 5}
            mock_clear.return_value = mock_result
            
            response = client.post("/api/v1/hackrx/clear-cache", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
    
    def test_system_stats_endpoint(self):
        """Test system stats endpoint"""
        headers = {
            "Authorization": "Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"
        }
        
        with patch('app.services.query_processor.QueryProcessor.get_system_stats') as mock_stats:
            mock_result = {"system_status": "healthy", "test": "data"}
            mock_stats.return_value = mock_result
            
            response = client.get("/api/v1/hackrx/stats", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["system_status"] == "healthy"
    
    def test_embedding_stats_endpoint(self):
        """Test embedding stats endpoint"""
        headers = {
            "Authorization": "Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"
        }
        
        with patch('app.services.embedding_service.EmbeddingService.get_embedding_stats') as mock_stats:
            mock_result = {"total_vector_count": 100, "dimension": 384}
            mock_stats.return_value = mock_result
            
            response = client.get("/api/v1/hackrx/embedding-stats", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert "total_vector_count" in data
    
    def test_test_endpoints(self):
        """Test utility endpoints for testing"""
        headers = {
            "Authorization": "Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60"
        }
        
        # Test document processing
        with patch('app.services.document_processor.DocumentProcessor.process_document') as mock_process:
            mock_chunks = [Mock(content="Test content")]
            mock_process.return_value = mock_chunks
            
            response = client.post(
                "/api/v1/hackrx/test-document-processing",
                params={"document_url": "https://example.com/test.pdf"},
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
        
        # Test embeddings
        with patch('app.services.embedding_service.EmbeddingService.create_single_embedding') as mock_embed:
            mock_embedding = [0.1] * 384
            mock_embed.return_value = mock_embedding
            
            response = client.post(
                "/api/v1/hackrx/test-embeddings",
                params={"text": "Test text"},
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["embedding_dimension"] == 384

if __name__ == "__main__":
    pytest.main([__file__]) 