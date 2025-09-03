# ChromaDB Integration for AIDE Backend

This document describes the ChromaDB integration that replaces the previous FAISS-based vector store in the AIDE backend system.

## Overview

The AIDE backend has been upgraded from FAISS to ChromaDB for improved vector storage and retrieval capabilities. ChromaDB provides:

- **Persistent Storage**: Vector embeddings are stored persistently on disk
- **Better Metadata Management**: Rich metadata support for documents
- **Improved Search**: More sophisticated similarity search algorithms
- **Scalability**: Better handling of large document collections
- **Easier Management**: Built-in collection management and statistics

## Key Changes

### 1. Vector Store Implementation

- **File**: `rag/vector_store.py`
- **Class**: `ChromaDBVectorStore` (replaces `FAISSVectorStore`)
- **Backward Compatibility**: `FAISSVectorStore` is aliased to `ChromaDBVectorStore`

### 2. Configuration Updates

- **File**: `utils/config.py`
- **New Settings**:
  - `CHROMADB_COLLECTION_NAME`: Name of the ChromaDB collection
  - `CHROMADB_PERSIST_DIRECTORY`: Directory for persistent storage
  - `CHROMADB_DISTANCE_METRIC`: Distance metric for similarity search

### 3. Dependencies

New dependencies added to `requirements.txt`:
```
chromadb==0.4.22
sentence-transformers==2.5.1
numpy>=1.24.0
langchain==0.2.0
langchain-community==0.2.0
langchain-groq==0.1.0
```

## Architecture

### ChromaDB Vector Store

```python
class ChromaDBVectorStore:
    def __init__(self, store_path, embedding_manager, collection_name="documents")
    
    # Core methods
    def add_documents(self, documents, chunk_size=1000, chunk_overlap=200)
    def similarity_search(self, query, k=5, threshold=0.7)
    def get_document_count(self)
    def rebuild_index(self, knowledge_base_path)
    
    # Additional features
    def delete_documents(self, document_ids)
    def update_document(self, document_id, new_content, new_metadata)
    def get_collection_info(self)
```

### Document Processing

1. **Chunking**: Documents are split into chunks using `RecursiveCharacterTextSplitter`
2. **Embedding**: Each chunk is converted to embeddings using the sentence transformer model
3. **Storage**: Chunks, embeddings, and metadata are stored in ChromaDB collections
4. **Retrieval**: Similarity search using cosine distance with configurable thresholds

### Metadata Structure

Each document chunk includes rich metadata:
```python
{
    'source': 'file_path',
    'title': 'document_title',
    'category': 'document_category',
    'chunk_index': 0,
    'total_chunks': 5,
    'original_metadata': {...},
    'chunk_size': 1000,
    'document_type': 'text'
}
```

## Usage

### Basic Initialization

```python
from rag.vector_store import ChromaDBVectorStore
from rag.embeddings import EmbeddingManager

# Initialize embedding manager
embedding_manager = EmbeddingManager()

# Initialize ChromaDB vector store
vector_store = ChromaDBVectorStore(
    store_path="data/vector_store",
    embedding_manager=embedding_manager,
    collection_name="documents"
)
```

### Adding Documents

```python
documents = [
    {
        'content': 'Document content here...',
        'source': 'document.txt',
        'title': 'Document Title',
        'category': 'general'
    }
]

vector_store.add_documents(documents, chunk_size=1000, chunk_overlap=200)
```

### Searching Documents

```python
results = vector_store.similarity_search(
    query="academic rules",
    k=5,
    threshold=0.7
)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Similarity: {result['similarity_score']}")
    print(f"Metadata: {result['metadata']}")
```

## Configuration

### Environment Variables

Create a `.env` file with the following settings:

```bash
# Flask Configuration
FLASK_ENV=development
PORT=5001

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=aide_db

# RAG Configuration
GROQ_API_KEY=your_groq_api_key_here  # Optional, will use fallback if not provided
```

### ChromaDB Settings

Default ChromaDB configuration in `utils/config.py`:
```python
CHROMADB_COLLECTION_NAME = "documents"
CHROMADB_PERSIST_DIRECTORY = "data/vector_store"
CHROMADB_DISTANCE_METRIC = "cosine"
```

## Migration from FAISS

### What Changed

1. **Storage Format**: From FAISS index files to ChromaDB persistent storage
2. **File Structure**: 
   - Old: `faiss_index`, `documents.pkl`, `metadata.pkl`
   - New: ChromaDB database files in `data/vector_store/`
3. **API**: Same interface, enhanced functionality

### Migration Process

1. **Automatic**: The system automatically migrates on first run
2. **Manual**: Old FAISS files are automatically cleaned up
3. **Data Preservation**: All document content and metadata is preserved

## Performance Considerations

### Embedding Generation

- **Model**: Uses `sentence-transformers/all-MiniLM-L6-v2` by default
- **Dimension**: 384-dimensional embeddings
- **Optimization**: Batch processing for multiple documents

### Search Performance

- **Index Type**: HNSW (Hierarchical Navigable Small World) for fast approximate search
- **Distance Metric**: Cosine similarity for better semantic matching
- **Threshold Filtering**: Configurable similarity thresholds

### Storage

- **Persistent**: Embeddings stored on disk for fast retrieval
- **Compression**: Efficient storage of vector data
- **Metadata**: Rich metadata without performance impact

## Troubleshooting

### Common Issues

1. **ChromaDB Import Error**
   ```bash
   pip install chromadb==0.4.22
   ```

2. **Memory Issues with Large Documents**
   - Reduce `chunk_size` in configuration
   - Process documents in smaller batches

3. **Search Quality Issues**
   - Adjust similarity threshold
   - Check embedding model quality
   - Verify document chunking

### Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

Use the built-in health check endpoints:
- `/api/rag/health` - RAG system status
- `/api/mongodb/health` - MongoDB status

## Testing

### Quick Test

```bash
# Activate virtual environment
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

### Test Endpoints

1. **Health Check**: `GET /api/health`
2. **RAG Status**: `GET /api/rag/health`
3. **Chat**: `POST /api/rag/chat`

## Future Enhancements

### Planned Features

1. **Multiple Collections**: Support for domain-specific collections
2. **Advanced Filtering**: Metadata-based document filtering
3. **Hybrid Search**: Combine vector and keyword search
4. **Real-time Updates**: Live document updates without rebuilding
5. **Performance Monitoring**: Detailed performance metrics

### Integration Possibilities

1. **LangChain Integration**: Enhanced LangChain compatibility
2. **Custom Embeddings**: Support for custom embedding models
3. **Multi-modal**: Support for images and other media types
4. **Distributed**: Multi-node ChromaDB deployment

## Support

For issues or questions:

1. Check the logs in `logs/` directory
2. Verify configuration in `.env` file
3. Test individual components using the test scripts
4. Check ChromaDB documentation for advanced features

## Conclusion

The ChromaDB integration provides a robust, scalable foundation for the AIDE backend's vector storage needs. The migration maintains backward compatibility while adding significant new capabilities for document management and retrieval.
