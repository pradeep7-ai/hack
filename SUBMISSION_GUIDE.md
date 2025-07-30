# HackRx 6.0 - Submission Guide

## 🎯 Project Overview

**HackRx 6.0 - LLM-Powered Intelligent Query-Retrieval System**

This project implements a comprehensive RAG (Retrieval-Augmented Generation) system designed specifically for processing insurance, legal, HR, and compliance documents. The system can understand complex queries and provide accurate, contextual answers with explainable reasoning.

## 🏗️ System Architecture

```
Input Documents (PDF/DOCX/Email)
    ↓
LLM Parser (Extract structured query)
    ↓
Embedding Search (Pinecone/FAISS retrieval)
    ↓
Clause Matching (Semantic similarity)
    ↓
Logic Evaluation (Decision processing)
    ↓
JSON Output (Structured response)
```

## 🚀 Key Features

### 1. **Multi-format Document Processing**

- PDF, DOCX, and email document support
- Intelligent text extraction and cleaning
- Optimal chunking strategy with overlap

### 2. **Semantic Search & Retrieval**

- Pinecone vector database integration
- Sentence Transformers for embeddings
- Context-aware similarity matching

### 3. **LLM-Powered Answer Generation**

- OpenAI GPT-4 integration
- Structured query extraction
- Context-aware prompt engineering

### 4. **Explainable Decisions**

- Detailed reasoning for each answer
- Source traceability
- Validation and confidence scoring

### 5. **Performance Optimizations**

- Token efficiency management
- Caching mechanisms
- Batch processing capabilities

## 📋 Evaluation Criteria Alignment

### ✅ **Accuracy**

- Precision query understanding through structured extraction
- Semantic clause matching with configurable similarity thresholds
- Multi-stage validation pipeline

### ✅ **Token Efficiency**

- Smart chunking strategy (1000 chars with 200 overlap)
- Context-aware prompt engineering
- Token usage monitoring and optimization

### ✅ **Latency**

- Async processing pipeline
- Document caching
- Optimized embedding generation

### ✅ **Reusability**

- Modular service architecture
- Configurable parameters
- Extensible plugin system

### ✅ **Explainability**

- Detailed metadata in responses
- Source attribution
- Reasoning chain documentation

## 🛠️ Technical Implementation

### Core Services

1. **DocumentProcessor** (`app/services/document_processor.py`)

   - Multi-format document handling
   - Intelligent text extraction
   - Optimal chunking strategy

2. **EmbeddingService** (`app/services/embedding_service.py`)

   - Vector embedding generation
   - Pinecone integration
   - Semantic search capabilities

3. **LLMService** (`app/services/llm_service.py`)

   - OpenAI GPT-4 integration
   - Context-aware prompting
   - Answer validation

4. **QueryProcessor** (`app/services/query_processor.py`)
   - Main orchestration service
   - Pipeline management
   - Error handling

### API Endpoints

- `POST /api/v1/hackrx/run` - Main submission endpoint
- `GET /api/v1/hackrx/health` - System health check
- `GET /api/v1/hackrx/stats` - System statistics
- `POST /api/v1/hackrx/single-question` - Single question processing
- Additional utility endpoints for testing and monitoring

## 📊 Sample Response Format

```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
    "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months."
  ],
  "metadata": {
    "document_id": "uuid",
    "chunk_count": 45,
    "total_processing_time": 12.5,
    "average_processing_time_per_question": 4.2,
    "processing_details": [
      {
        "question_index": 0,
        "search_results_count": 5,
        "processing_time": 3.8,
        "token_usage": 1250,
        "validation_score": 9.2
      }
    ]
  }
}
```

## 🧪 Testing & Validation

### Automated Tests

- Unit tests for all services
- API endpoint testing
- Integration tests
- Performance benchmarks

### Manual Testing

- Sample document processing
- Query accuracy validation
- Performance monitoring
- Error handling verification

## 📈 Performance Metrics

### Document Processing

- **PDF Processing**: ~2-5 seconds per page
- **Chunking**: 1000 characters with 200 overlap
- **Embedding Generation**: ~0.1 seconds per chunk

### Query Processing

- **Search Time**: ~0.5-1 second per query
- **LLM Response**: ~2-5 seconds per answer
- **Total Pipeline**: ~3-8 seconds per question

### Token Efficiency

- **Input Tokens**: ~500-1000 per query
- **Output Tokens**: ~200-500 per answer
- **Total Cost**: Optimized for cost-effectiveness

## 🔧 Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd hackrx-6.0

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
```

### 3. Database Setup

```bash
# Initialize database
alembic upgrade head
```

### 4. Run Application

```bash
# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test the System

```bash
# Run demo script
python test_demo.py

# Run tests
pytest tests/
```

## 🎯 Hackathon Submission

### Required Files

- ✅ Complete source code
- ✅ API documentation
- ✅ Test suite
- ✅ Performance metrics
- ✅ Setup instructions

### API Endpoint for Submission

```
POST http://localhost:8000/api/v1/hackrx/run
Content-Type: application/json
Authorization: Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60

{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=...",
    "questions": [
        "What is the grace period for premium payment?",
        "Does this policy cover knee surgery?"
    ]
}
```

### Expected Response

```json
{
  "answers": [
    "A grace period of thirty days is provided...",
    "Yes, the policy covers knee surgery under the following conditions..."
  ]
}
```

## 🏆 Competitive Advantages

1. **Comprehensive RAG Pipeline**: Complete implementation from document processing to answer generation
2. **Insurance Domain Expertise**: Specialized prompts and validation for insurance documents
3. **Explainable AI**: Detailed reasoning and source attribution
4. **Performance Optimized**: Efficient token usage and caching strategies
5. **Production Ready**: Error handling, monitoring, and scalability considerations
6. **Extensible Architecture**: Easy to extend for other domains (legal, HR, compliance)

## 📚 Documentation

- **API Documentation**: Available at `http://localhost:8000/docs`
- **Code Comments**: Comprehensive inline documentation
- **README.md**: Detailed setup and usage instructions
- **Test Suite**: Validates all functionality

## 🔮 Future Enhancements

1. **Multi-language Support**: Extend to support multiple languages
2. **Advanced Caching**: Redis integration for better performance
3. **Real-time Processing**: WebSocket support for streaming responses
4. **Custom Models**: Fine-tuned models for specific domains
5. **Advanced Analytics**: Detailed usage analytics and insights

---

**Team**: HackRx 6.0 Team  
**Submission Date**: January 2024  
**Category**: LLM-Powered Intelligent Query-Retrieval System
