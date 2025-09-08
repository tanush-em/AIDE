# Backend API Endpoints Documentation

## Base URL
- **Backend**: `http://localhost:5001`
- **Frontend**: `http://localhost:3000`

## Main App Endpoints (`/`)

### Health & Status
- `GET /` - Home endpoint, returns basic status
- `GET /api/health` - Main health check with available endpoints
- `GET /api/data` - Sample data endpoint

## RAG API Endpoints (`/api/rag`)

### Chat & Conversation
- `POST /api/rag/chat` - **Main chat endpoint** - Handle chat messages with RAG system
- `GET /api/rag/history/<session_id>` - Get conversation history for a session
- `DELETE /api/rag/clear/<session_id>` - Clear a conversation session

### System Management
- `GET /api/rag/status` - Get RAG system status
- `GET /api/rag/health` - Health check for RAG system
- `GET /api/rag/simple-health` - Simple health check (no RAG service required)
- `POST /api/rag/rebuild` - Rebuild the knowledge base
- `POST /api/rag/cleanup` - Clean up inactive sessions

### Data Export
- `GET /api/rag/export/<session_id>` - Export conversation session (format: json, txt)

## MongoDB API Endpoints (`/api/mongodb`)

### Health & Status
- `GET /api/mongodb/health` - Health check for MongoDB system
- `GET /api/mongodb/stats` - Get database statistics

### Document Management
- `GET /api/mongodb/documents` - Get documents with optional filters
  - Query params: `limit`, `type`, `category`, `status`
- `POST /api/mongodb/documents` - Create a new document
- `GET /api/mongodb/documents/<document_id>` - Get a specific document
- `PUT /api/mongodb/documents/<document_id>` - Update a document
- `POST /api/mongodb/documents/search` - Search documents by text

### User Management
- `GET /api/mongodb/users` - Get users with optional filters
  - Query params: `limit`, `role`, `status`
- `POST /api/mongodb/users` - Create a new user
- `GET /api/mongodb/users/<user_id>` - Get a specific user
- `PUT /api/mongodb/users/<user_id>` - Update a user

### Analytics & Logs
- `GET /api/mongodb/analytics` - Get analytics with optional filters
  - Query params: `limit`, `event_type`, `source`
- `GET /api/mongodb/query-logs` - Get query logs with optional filters
  - Query params: `limit`, `query_type`, `success`

### Agent Tools
- `POST /api/mongodb/tools/search` - Search database using MongoDB tools
- `POST /api/mongodb/tools/aggregate` - Perform aggregation using MongoDB tools
- `POST /api/mongodb/tools/view-record` - View a specific record
- `POST /api/mongodb/tools/edit-record` - Edit a record
- `POST /api/mongodb/tools/create-record` - Create a record

## Request/Response Format

### Chat Request
```json
{
  "message": "string",
  "session_id": "string (optional)",
  "user_id": "string (optional, default: 'default')"
}
```

### Chat Response
```json
{
  "session_id": "string",
  "response": "string",
  "confidence": "high|medium|low",
  "suggestions": ["string"],
  "agent_status": "object",
  "conversation_length": "number",
  "session_active": "boolean"
}
```

### Error Response
```json
{
  "error": "string"
}
```

## CORS Configuration
The backend allows requests from:
- `http://localhost:3000` (Next.js frontend)
- `http://localhost:3001` (Alternative frontend port)
- `http://localhost:5001` (Backend itself)

## Port Configuration
- **Backend**: Port 5001 (configurable via environment variable `PORT`)
- **Frontend**: Port 3000 (Next.js default)

## Environment Variables
Create a `.env` file in the backend directory with:
```
FLASK_ENV=development
PORT=5001
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=aide_db
GROQ_API_KEY=your_api_key_here
```

## Testing Endpoints
For testing and debugging, use:
- `POST /api/rag/chat` - Main chat endpoint
- `GET /api/health` - Basic health check with endpoint information
- `GET /api/rag/simple-health` - RAG health without initialization

## Logging
The backend now includes comprehensive logging for all endpoints:
- All requests are logged with timestamps
- Errors include full stack traces
- Processing steps are logged for debugging
- Logs are written to both console and `server.log` file
