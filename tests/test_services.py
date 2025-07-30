import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.models import DocumentChunk, SearchResult

class TestDocumentProcessor:
    """Test cases for DocumentProcessor service"""
    
    def setup_method(self):
        self.processor = DocumentProcessor()
    
    def test_initialization(self):
        """Test DocumentProcessor initialization"""
        assert ".pdf" in self.processor.supported_formats
        assert ".docx" in self.processor.supported_formats
        assert self.processor.chunk_size == 1000
        assert self.processor.chunk_overlap == 200
    
    def test_get_file_extension(self):
        """Test file extension extraction"""
        # Test PDF
        url = "https://example.com/document.pdf?param=value"
        ext = self.processor.get_file_extension(url)
        assert ext == ".pdf"
        
        # Test DOCX
        url = "https://example.com/document.docx"
        ext = self.processor.get_file_extension(url)
        assert ext == ".docx"
        
        # Test with no extension
        url = "https://example.com/document"
        ext = self.processor.get_file_extension(url)
        assert ext == ""
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        dirty_text = "  This   is   a   test   text   with   extra   spaces.  "
        clean_text = self.processor.clean_text(dirty_text)
        assert clean_text == "This is a test text with extra spaces."
        
        # Test with special characters
        dirty_text = "Text with @#$%^&*() special chars"
        clean_text = self.processor.clean_text(dirty_text)
        assert "special chars" in clean_text
    
    def test_chunk_text(self):
        """Test text chunking functionality"""
        text = "This is a test text. It has multiple sentences. We want to chunk it properly."
        
        chunks = self.processor.chunk_text(text, chunk_size=20, overlap=5)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
        assert all(chunk.content for chunk in chunks)
        assert all(chunk.chunk_id for chunk in chunks)
    
    @patch('app.services.document_processor.requests.get')
    def test_download_document_success(self, mock_get):
        """Test successful document download"""
        mock_response = Mock()
        mock_response.content = b"test content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        content = self.processor.download_document("https://example.com/test.pdf")
        assert content == b"test content"
    
    @patch('app.services.document_processor.requests.get')
    def test_download_document_failure(self, mock_get):
        """Test document download failure"""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Failed to download document"):
            self.processor.download_document("https://example.com/test.pdf")
    
    @patch('app.services.document_processor.fitz.open')
    def test_extract_text_from_pdf(self, mock_fitz_open):
        """Test PDF text extraction"""
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "PDF content"
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc
        
        content = b"fake pdf content"
        text = self.processor.extract_text_from_pdf(content)
        
        assert "PDF content" in text
        mock_doc.close.assert_called_once()
    
    @patch('app.services.document_processor.DocxDocument')
    def test_extract_text_from_docx(self, mock_docx):
        """Test DOCX text extraction"""
        mock_doc = Mock()
        mock_paragraph = Mock()
        mock_paragraph.text = "DOCX content"
        mock_doc.paragraphs = [mock_paragraph]
        mock_docx.return_value = mock_doc
        
        content = b"fake docx content"
        text = self.processor.extract_text_from_docx(content)
        
        assert "DOCX content" in text

class TestEmbeddingService:
    """Test cases for EmbeddingService"""
    
    def setup_method(self):
        with patch.dict(os.environ, {'PINECONE_API_KEY': 'test_key', 'PINECONE_ENVIRONMENT': 'test_env'}):
            self.service = EmbeddingService()
    
    def test_initialization(self):
        """Test EmbeddingService initialization"""
        assert self.service.model_name == "all-MiniLM-L6-v2"
        assert hasattr(self.service, 'model')
        assert hasattr(self.service, 'tokenizer')
    
    def test_count_tokens(self):
        """Test token counting"""
        text = "This is a test text for token counting."
        token_count = self.service.count_tokens(text)
        assert isinstance(token_count, int)
        assert token_count > 0
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_create_embeddings(self, mock_transformer):
        """Test embedding creation"""
        mock_model = Mock()
        mock_embeddings = Mock()
        mock_embeddings.tolist.return_value = [[0.1, 0.2, 0.3]] * 3
        mock_model.encode.return_value = mock_embeddings
        mock_transformer.return_value = mock_model
        
        self.service.model = mock_model
        
        texts = ["text1", "text2", "text3"]
        embeddings = self.service.create_embeddings(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 3 for emb in embeddings)
    
    def test_create_single_embedding(self):
        """Test single embedding creation"""
        with patch.object(self.service, 'create_embeddings') as mock_create:
            mock_create.return_value = [[0.1, 0.2, 0.3]]
            
            embedding = self.service.create_single_embedding("test text")
            assert embedding == [0.1, 0.2, 0.3]
    
    def test_store_embeddings_no_pinecone(self):
        """Test embedding storage when Pinecone is not available"""
        self.service.index = None
        
        chunks = [
            DocumentChunk(content="chunk1", chunk_id="id1"),
            DocumentChunk(content="chunk2", chunk_id="id2")
        ]
        
        with patch.object(self.service, 'create_embeddings') as mock_create:
            mock_create.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            
            embedding_ids = self.service.store_embeddings(chunks, "doc123")
            assert len(embedding_ids) == 2
            assert all("mock_embedding" in id for id in embedding_ids)
    
    def test_search_similar_no_pinecone(self):
        """Test similarity search when Pinecone is not available"""
        self.service.index = None
        
        results = self.service.search_similar("test query")
        assert len(results) == 1
        assert results[0].content == "Mock search result content for demonstration purposes."
        assert results[0].score == 0.95

class TestLLMService:
    """Test cases for LLMService"""
    
    def setup_method(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            self.service = LLMService()
    
    def test_initialization(self):
        """Test LLMService initialization"""
        assert self.service.model == "gpt-4"
        assert self.service.max_tokens == 1000
        assert self.service.temperature == 0.1
    
    def test_count_tokens(self):
        """Test token counting estimation"""
        text = "This is a test text for token counting estimation."
        token_count = self.service.count_tokens(text)
        assert isinstance(token_count, int)
        assert token_count > 0
    
    def test_create_context_prompt(self):
        """Test context prompt creation"""
        query = "What is covered?"
        search_results = [
            SearchResult(content="Coverage includes hospitalization", score=0.9, source="doc1"),
            SearchResult(content="Policy covers surgery", score=0.8, source="doc1")
        ]
        
        prompt = self.service.create_context_prompt(query, search_results)
        
        assert "What is covered?" in prompt
        assert "Coverage includes hospitalization" in prompt
        assert "Policy covers surgery" in prompt
        assert "Instructions:" in prompt
    
    @patch('app.services.llm_service.OpenAI')
    def test_generate_answer(self, mock_openai):
        """Test answer generation"""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "Test answer"
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        self.service.client = mock_client
        
        search_results = [
            SearchResult(content="Test context", score=0.9, source="doc1")
        ]
        
        result = self.service.generate_answer("Test question", search_results)
        
        assert "answer" in result
        assert result["answer"] == "Test answer"
        assert "processing_time" in result
        assert "total_tokens" in result
    
    @patch('app.services.llm_service.OpenAI')
    def test_extract_structured_query(self, mock_openai):
        """Test structured query extraction"""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = '{"query_type": "coverage", "key_terms": ["coverage"]}'
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        self.service.client = mock_client
        
        result = self.service.extract_structured_query("What is covered?")
        
        assert "query_type" in result
        assert result["query_type"] == "coverage"
    
    def test_extract_structured_query_fallback(self):
        """Test structured query extraction fallback"""
        with patch.object(self.service, 'client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API error")
            
            result = self.service.extract_structured_query("What is covered?")
            
            assert "query_type" in result
            assert result["query_type"] == "general"
            assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__]) 