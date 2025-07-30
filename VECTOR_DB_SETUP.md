# Vector Database Setup Guide

This guide will help you set up and configure the vector database for your HackRx application.

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 2: Configure Environment

1. Copy the environment template:

```bash
cp env.example .env
```

2. Edit `.env` file and configure:

   - **For FAISS only (recommended for development):**

     ```
     VECTOR_STORE_TYPE=faiss
     # Leave Pinecone settings empty
     ```

   - **For Pinecone (if you have API keys):**

     ```
     VECTOR_STORE_TYPE=pinecone
     PINECONE_API_KEY=your_api_key_here
     PINECONE_ENVIRONMENT=your_environment_here
     PINECONE_INDEX_NAME=hackrx-documents
     ```

   - **For both (recommended for production):**
     ```
     VECTOR_STORE_TYPE=both
     PINECONE_API_KEY=your_api_key_here
     PINECONE_ENVIRONMENT=your_environment_here
     ```

### Step 3: Test the Setup

Run the setup script to test your configuration:

```bash
python setup_vector_db.py
```

This will:

- ✅ Test document processing
- ✅ Test embedding creation
- ✅ Test vector storage
- ✅ Test vector search
- ✅ Show statistics

### Step 4: Start Your Application

```bash
# Start the FastAPI server
uvicorn main:app --reload
```

## 🔧 Vector Database Options

### Option 1: FAISS (Local - No API Keys Required)

**Pros:**

- ✅ No API keys required
- ✅ Works offline
- ✅ Fast and efficient
- ✅ Free to use
- ✅ Data stays local

**Cons:**

- ❌ Limited to local storage
- ❌ No cloud backup
- ❌ Manual scaling

**Best for:** Development, testing, small to medium projects

### Option 2: Pinecone (Cloud - API Keys Required)

**Pros:**

- ✅ Scalable cloud solution
- ✅ Automatic backups
- ✅ High availability
- ✅ Advanced features

**Cons:**

- ❌ Requires API keys
- ❌ Monthly costs
- ❌ Internet dependency

**Best for:** Production, large-scale applications

### Option 3: Both (Hybrid - Recommended)

**Pros:**

- ✅ Best of both worlds
- ✅ Fallback capability
- ✅ Flexible deployment

**Cons:**

- ❌ More complex setup
- ❌ Higher resource usage

**Best for:** Production with redundancy

## 📊 Understanding the Results

### Setup Script Output

When you run `python setup_vector_db.py`, you'll see:

```
🚀 Vector Database Setup
==================================================
📄 Testing Document Processing...
✅ Created 3 chunks from sample text
  Chunk 1: 150 characters
  Chunk 2: 180 characters
  Chunk 3: 120 characters

🔧 Testing Vector Store Setup...
📦 Initializing Vector Store...
📊 Vector Store Stats:
  pinecone_available: False
  faiss_available: True
  faiss_vector_count: 0

🧠 Testing Embedding Creation...
✅ Created 3 embeddings
📏 Embedding dimension: 384

💾 Testing Embedding Storage...
✅ Stored 3 embeddings

🔍 Testing Vector Search...
✅ Found 3 results
  Result 1: Score=0.856
    Content: This is a test document about health insurance...
  Result 2: Score=0.723
    Content: The policy covers maternity expenses...
  Result 3: Score=0.689
    Content: Grace period is thirty days...

🎉 Vector Store Setup Complete!

==================================================
📋 Setup Summary:
  Document Processing: ✅ PASS
  Vector Store: ✅ PASS

🎉 All tests passed! Your vector database is ready.
```

### What Each Test Means

1. **Document Processing**: Tests text chunking and cleaning
2. **Vector Store Initialization**: Tests FAISS/Pinecone setup
3. **Embedding Creation**: Tests AI model for creating vectors
4. **Embedding Storage**: Tests saving vectors to database
5. **Vector Search**: Tests similarity search functionality

## 🛠️ Troubleshooting

### Common Issues

#### 1. "No vector store available" Error

**Solution:**

```bash
# Make sure FAISS is installed
pip install faiss-cpu

# Or for GPU support (if available)
pip install faiss-gpu
```

#### 2. "Pinecone initialization failed" Error

**Solution:**

- Check your Pinecone API keys in `.env`
- Verify your Pinecone environment
- Or use FAISS only by setting `VECTOR_STORE_TYPE=faiss`

#### 3. "Failed to create embeddings" Error

**Solution:**

```bash
# Install sentence transformers
pip install sentence-transformers

# Or reinstall all dependencies
pip install -r requirements.txt
```

#### 4. Permission Errors

**Solution:**

```bash
# Make sure you have write permissions
chmod 755 vector_store/
```

### Performance Optimization

#### For Large Documents

1. **Increase chunk size** in `.env`:

   ```
   CHUNK_SIZE=2000
   CHUNK_OVERLAP=400
   ```

2. **Use batch processing**:
   ```python
   # Process in smaller batches
   embedding_service.batch_process_chunks(chunks, batch_size=50)
   ```

#### For Better Search Results

1. **Adjust top_k parameter**:

   ```python
   results = embedding_service.search_similar(query, top_k=10)
   ```

2. **Use filters**:
   ```python
   results = embedding_service.search_similar(
       query,
       top_k=5,
       filter_dict={"document_id": "specific_doc"}
   )
   ```

## 📁 File Structure

After setup, you'll have:

```
hacka/
├── app/
│   ├── services/
│   │   ├── vector_store.py      # New unified vector store
│   │   ├── embedding_service.py # Updated to use vector store
│   │   └── document_processor.py
│   └── ...
├── vector_store/                 # FAISS storage directory
│   ├── faiss_index.bin         # FAISS index file
│   └── metadata.pkl            # Document metadata
├── setup_vector_db.py           # Setup and test script
├── requirements.txt             # Updated dependencies
└── .env                        # Environment configuration
```

## 🎯 Next Steps

1. **Test with your documents**:

   ```bash
   # Upload a document through your API
   curl -X POST "http://localhost:8000/api/upload" \
        -F "file=@your_document.pdf"
   ```

2. **Test search functionality**:

   ```bash
   # Search for information
   curl -X POST "http://localhost:8000/api/search" \
        -H "Content-Type: application/json" \
        -d '{"query": "What is the grace period?"}'
   ```

3. **Monitor performance**:
   ```python
   # Check vector store statistics
   stats = embedding_service.get_embedding_stats()
   print(stats)
   ```

## 🔄 Updating Existing Code

If you have existing code using the old embedding service, the interface remains the same:

```python
from app.services.embedding_service import EmbeddingService

# Initialize (now uses unified vector store)
embedding_service = EmbeddingService()

# Store embeddings (works with FAISS and/or Pinecone)
embedding_ids = embedding_service.store_embeddings(chunks, document_id)

# Search (works with FAISS and/or Pinecone)
results = embedding_service.search_similar("your query", top_k=5)
```

The new implementation is backward compatible and will automatically use the best available vector store based on your configuration.

## 🚀 Production Deployment

For production, consider:

1. **Use both FAISS and Pinecone** for redundancy
2. **Set up proper backups** for FAISS data
3. **Monitor vector store performance**
4. **Scale based on your needs**

```bash
# Production environment variables
VECTOR_STORE_TYPE=both
PINECONE_API_KEY=your_production_key
PINECONE_ENVIRONMENT=your_production_env
```

---

**🎉 Congratulations!** Your vector database is now properly configured and ready to use. The system will automatically choose the best available vector store based on your configuration and provide fallback options if needed.
