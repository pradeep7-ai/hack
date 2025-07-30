# HackRx 6.0 - LLM-Powered Intelligent Query-Retrieval System

## Problem Statement

Design an LLM-Powered Intelligent Query–Retrieval System that can process large documents and make contextual decisions for insurance, legal, HR, and compliance domains.

## System Architecture

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

## Features

- **Multi-format Document Processing**: PDF, DOCX, and email documents
- **Semantic Search**: Using Pinecone vector database for efficient retrieval
- **Contextual Understanding**: LLM-powered query parsing and clause matching
- **Explainable Decisions**: Clear rationale for each response
- **Structured Output**: JSON responses with traceable reasoning
- **Token Optimization**: Efficient LLM usage for cost-effectiveness

## Tech Stack

- **Backend**: FastAPI
- **Vector Database**: Pinecone
- **LLM**: OpenAI GPT-4
- **Database**: PostgreSQL
- **Document Processing**: PyMuPDF, python-docx
- **Embeddings**: Sentence Transformers

## Setup Instructions

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   Create a `.env` file with:

   ```
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENVIRONMENT=your_pinecone_environment
   PINECONE_INDEX_NAME=hackrx-documents
   DATABASE_URL=postgresql://user:password@localhost/hackrx_db
   ```

3. **Initialize Database**:

   ```bash
   alembic upgrade head
   ```

4. **Run the Application**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### Base URL: `http://localhost:8000/api/v1`

### POST `/hackrx/run`

Process documents and answer questions.

**Headers**:

```
Content-Type: application/json
Accept: application/json
Authorization: Bearer a863b0e20b90a5c03973a305d4b966b43a6cc5a1b8292f0d5dfb226c42a5cf60
```

**Request Body**:

```json
{
  "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=...",
  "questions": [
    "What is the grace period for premium payment?",
    "Does this policy cover knee surgery?"
  ]
}
```

**Response**:

```json
{
  "answers": [
    "A grace period of thirty days is provided...",
    "Yes, the policy covers knee surgery under the following conditions..."
  ]
}
```

## Evaluation Criteria

- **Accuracy**: Precision of query understanding and clause matching
- **Token Efficiency**: Optimized LLM token usage
- **Latency**: Response speed and real-time performance
- **Reusability**: Code modularity and extensibility
- **Explainability**: Clear decision reasoning and clause traceability

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── models.py          # Pydantic models
│   ├── database.py        # Database configuration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_processor.py  # Document parsing
│   │   ├── embedding_service.py   # Vector embeddings
│   │   ├── llm_service.py         # LLM interactions
│   │   └── query_processor.py     # Query processing
│   └── api/
│       ├── __init__.py
│       └── hackrx.py      # API endpoints
├── tests/                 # Test files
├── alembic/              # Database migrations
└── requirements.txt      # Dependencies
```

## Testing

Run tests with:

```bash
pytest tests/
```

## Performance Optimizations

- **Chunking Strategy**: Optimal document chunking for better retrieval
- **Caching**: Redis caching for frequently accessed embeddings
- **Batch Processing**: Efficient batch operations for multiple documents
- **Token Management**: Smart token usage to minimize costs
