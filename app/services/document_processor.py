import requests
import PyPDF2
from docx import Document as DocxDocument
import io
import hashlib
import uuid
from typing import List, Dict, Any, Optional
import re
from pathlib import Path

from app.models import DocumentChunk

class DocumentProcessor:
    """Service for processing various document formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc']
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # overlap between chunks
    
    def download_document(self, url: str) -> bytes:
        """Download document from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise Exception(f"Failed to download document from {url}: {str(e)}")
    
    def get_file_extension(self, url: str) -> str:
        """Extract file extension from URL"""
        path = Path(url.split('?')[0])  # Remove query parameters
        return path.suffix.lower()
    
    def extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text()
                text += "\n\n"  # Add spacing between pages
            
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX content"""
        try:
            doc = DocxDocument(io.BytesIO(content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', ' ', text)
        
        # Normalize spacing
        text = ' '.join(text.split())
        
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[DocumentChunk]:
        """Split text into overlapping chunks"""
        if chunk_size is None:
            chunk_size = self.chunk_size
        if overlap is None:
            overlap = self.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(start + chunk_size - 100, start)
                sentence_end = text.rfind('.', search_start, end)
                if sentence_end > start + chunk_size // 2:  # Only break if we find a reasonable boundary
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunk_id = str(uuid.uuid4())
                chunk = DocumentChunk(
                    content=chunk_text,
                    chunk_id=chunk_id,
                    metadata={
                        "start_pos": start,
                        "end_pos": end,
                        "length": len(chunk_text)
                    }
                )
                chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_document(self, url: str) -> List[DocumentChunk]:
        """Main method to process a document from URL"""
        try:
            # Download document
            content = self.download_document(url)
            
            # Determine file type
            file_ext = self.get_file_extension(url)
            
            if file_ext not in self.supported_formats:
                raise Exception(f"Unsupported file format: {file_ext}")
            
            # Extract text based on file type
            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(content)
            elif file_ext in ['.docx', '.doc']:
                text = self.extract_text_from_docx(content)
            else:
                raise Exception(f"Unsupported file format: {file_ext}")
            
            # Clean text
            text = self.clean_text(text)
            
            # Split into chunks
            chunks = self.chunk_text(text)
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Document processing failed: {str(e)}")
    
    def get_document_metadata(self, url: str, content: bytes) -> Dict[str, Any]:
        """Extract metadata from document"""
        try:
            file_ext = self.get_file_extension(url)
            file_hash = hashlib.md5(content).hexdigest()
            
            metadata = {
                "url": url,
                "file_type": file_ext,
                "file_size": len(content),
                "file_hash": file_hash,
                "processed_at": "2024-01-01T00:00:00Z"
            }
            
            if file_ext == '.pdf':
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                metadata.update({
                    "page_count": len(pdf_reader.pages),
                    "title": pdf_reader.metadata.get("/Title", "") if pdf_reader.metadata else "",
                    "author": pdf_reader.metadata.get("/Author", "") if pdf_reader.metadata else "",
                    "subject": pdf_reader.metadata.get("/Subject", "") if pdf_reader.metadata else ""
                })
            
            return metadata
            
        except Exception as e:
            return {
                "url": url,
                "file_type": file_ext,
                "error": str(e)
            } 