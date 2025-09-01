# MongoDB Integration for Enhanced RAG System

This document describes the MongoDB integration that has been added to your RAG system, providing dual data sources (vector store + MongoDB) with intelligent query routing.

## Architecture Overview

The enhanced system now supports:

1. **Dual Information Sources**:
   - **Static Knowledge**: Vectorized documents for semantic search (existing RAG)
   - **Dynamic Data**: MongoDB collections for structured queries and CRUD operations

2. **Intelligent Query Routing**: The system automatically determines whether to use RAG, MongoDB, or both based on query patterns

3. **Agent-Based Tools**: MongoDB operations are available as tools that agents can use

## Components

### 1. Database Layer (`database/`)

#### Connection Management (`connection.py`)
- Manages both async and sync MongoDB connections
- Handles connection pooling and health checks
- Provides connection status monitoring

#### Data Models (`models.py`)
- **User**: User management with roles and preferences
- **Document**: Document storage with metadata and categorization
- **Conversation**: Chat session management
- **Analytics**: Query and system analytics
- **QueryLog**: Detailed query logging for analysis

#### Service Layer (`mongodb_service.py`)
- CRUD operations for all collections
- Search and aggregation capabilities
- Analytics and logging functions
- Database statistics and health monitoring

### 2. Agent Tools (`agents/mongodb_tools.py`)

The system provides MongoDB-specific tools for agents:

- **`search_database_tool`**: Natural language search across collections
- **`view_record_tool`**: Retrieve specific records by ID
- **`edit_record_tool`**: Update existing records
- **`aggregate_data_tool`**: Complex queries and analytics
- **`create_record_tool`**: Create new records

### 3. Query Router (`agents/query_router.py`)

Intelligently routes queries based on patterns:

#### RAG Patterns (Conceptual/Explanatory)
- "What is...", "How to...", "Explain...", "Describe..."
- "What does the documentation say..."
- "Help me understand..."

#### MongoDB Patterns (Data Retrieval)
- "Show me...", "Find...", "Get...", "List..."
- "Count...", "Sum...", "Average..."
- "All users with...", "Recent entries..."

#### Combined Patterns
- "Explain X and show related data"
- "What is Y and find examples"

### 4. Enhanced RAG Service (`rag/enhanced_rag_service.py`)

Integrates both data sources:
- Routes queries to appropriate sources
- Combines results when needed
- Enhances RAG responses with MongoDB context
- Provides comprehensive analytics

## API Endpoints

### MongoDB Operations (`/api/mongodb/`)

#### Health and Status
- `GET /api/mongodb/health` - Database health check
- `GET /api/mongodb/stats` - Database statistics

#### Document Management
- `GET /api/mongodb/documents` - List documents with filters
- `POST /api/mongodb/documents` - Create new document
- `GET /api/mongodb/documents/<id>` - Get specific document
- `PUT /api/mongodb/documents/<id>` - Update document
- `POST /api/mongodb/documents/search` - Text search documents

#### User Management
- `GET /api/mongodb/users` - List users with filters
- `POST /api/mongodb/users` - Create new user
- `GET /api/mongodb/users/<id>` - Get specific user
- `PUT /api/mongodb/users/<id>` - Update user

#### Analytics and Logs
- `GET /api/mongodb/analytics` - Get analytics data
- `GET /api/mongodb/query-logs` - Get query logs

#### Agent Tools
- `POST /api/mongodb/tools/search` - Database search tool
- `POST /api/mongodb/tools/aggregate` - Aggregation tool
- `POST /api/mongodb/tools/view-record` - View record tool
- `POST /api/mongodb/tools/edit-record` - Edit record tool
- `POST /api/mongodb/tools/create-record` - Create record tool

### Enhanced Chat (`/api/enhanced-chat`)
- `POST /api/enhanced-chat` - Intelligent query routing with both RAG and MongoDB

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=aide_db
MONGODB_COLLECTIONS=users,documents,conversations,analytics

# RAG Configuration
RAG_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
RAG_EMBEDDING_DIMENSION=384
RAG_SIMILARITY_THRESHOLD=0.7
RAG_MAX_RESULTS=5

# Agent Configuration
AGENT_TIMEOUT=30
AGENT_MAX_RETRIES=3
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start MongoDB

Make sure MongoDB is running on your system:

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or using local installation
mongod
```

### 3. Seed Sample Data

```bash
cd backend
python seed_mongodb.py
```

### 4. Start the Backend

```bash
cd backend
python app.py
```

## Usage Examples

### 1. Conceptual Queries (RAG)
```
"What does the employee handbook say about workplace conduct?"
"How do I follow the data security guidelines?"
"Explain the project management best practices"
```

### 2. Data Retrieval Queries (MongoDB)
```
"Show me all active users"
"Find documents about security"
"Count the number of policies"
"List recent conversations"
```

### 3. Combined Queries
```
"Explain the employee handbook and show me related documents"
"What are the security guidelines and find examples of violations"
```

### 4. API Usage

#### Enhanced Chat
```bash
curl -X POST http://localhost:5001/api/enhanced-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all active users",
    "user_id": "john_doe"
  }'
```

#### MongoDB Search
```bash
curl -X POST http://localhost:5001/api/mongodb/tools/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "security guidelines",
    "collection": "documents",
    "limit": 5
  }'
```

## Query Routing Examples

### RAG Queries
- "What is the purpose of the employee handbook?"
- "How do I understand the security protocols?"
- "Explain the project management methodology"

### MongoDB Queries
- "Show me all users with admin role"
- "Find documents created this week"
- "Count active conversations"
- "List all policy documents"

### Combined Queries
- "Explain the security guidelines and show me related documents"
- "What are the best practices and find examples in our database"

## Analytics and Monitoring

The system automatically logs:
- Query patterns and routing decisions
- Processing times and performance metrics
- User interactions and session data
- System health and database statistics

Access analytics via:
- `GET /api/mongodb/analytics` - Query analytics
- `GET /api/mongodb/query-logs` - Detailed query logs
- `GET /api/mongodb/stats` - Database statistics

## Error Handling

The system includes comprehensive error handling:
- Connection failures with automatic retry
- Query parsing errors with fallback strategies
- Data validation and sanitization
- Graceful degradation when services are unavailable

## Performance Considerations

- **Connection Pooling**: Efficient MongoDB connection management
- **Async Operations**: Non-blocking database operations
- **Query Optimization**: Intelligent query routing reduces unnecessary processing
- **Caching**: Consider adding Redis for frequently accessed data
- **Indexing**: Ensure proper MongoDB indexes for collections

## Security

- **Input Validation**: All inputs are validated and sanitized
- **Access Control**: User-based permissions (can be extended)
- **Data Encryption**: Consider enabling MongoDB encryption
- **Audit Logging**: All operations are logged for audit purposes

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check if MongoDB is running
   - Verify connection string in `.env`
   - Check network connectivity

2. **Query Routing Issues**
   - Review query patterns in `query_router.py`
   - Check logs for routing decisions
   - Verify MongoDB data exists

3. **Performance Issues**
   - Monitor database statistics
   - Check query execution times
   - Consider adding indexes

### Debug Mode

Enable debug logging by setting:
```env
FLASK_ENV=development
```

## Future Enhancements

1. **Advanced NLP**: Integrate more sophisticated query understanding
2. **Machine Learning**: Learn from user interactions to improve routing
3. **Real-time Updates**: WebSocket support for live data updates
4. **Advanced Analytics**: Dashboard for system performance monitoring
5. **Multi-tenant Support**: Database partitioning for multiple organizations

## Support

For issues or questions:
1. Check the logs in the console output
2. Review the MongoDB connection status
3. Verify the data exists in the database
4. Test individual API endpoints

The enhanced system provides a powerful foundation for combining static knowledge with dynamic data, enabling more comprehensive and intelligent responses to user queries.
