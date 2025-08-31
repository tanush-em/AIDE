# Next.js + Flask Full-Stack Application with Agentic RAG System

This is a full-stack application with a Next.js frontend and Flask backend featuring an advanced **Agentic RAG (Retrieval-Augmented Generation) system** for academic management.

## Project Structure

```
├── frontend/          # Next.js application
│   ├── src/
│   │   ├── app/      # App router pages
│   │   └── components/ # React components
│   └── ...
├── backend/           # Flask application
│   ├── agents/       # RAG agent system
│   ├── rag/          # RAG infrastructure
│   ├── api/          # API endpoints
│   ├── utils/        # Utilities and config
│   ├── data/         # Knowledge base
│   └── ...
└── README.md         # This file
```

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- npm or yarn

## Setup Instructions

### Backend (Flask)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (copy from env.example):
   ```bash
   cp env.example .env
   ```

5. **Add your Groq API key** to the `.env` file:
   ```bash
   echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
   ```

6. Run the Flask application:
   ```bash
   python app.py
   ```

The backend will be available at `http://localhost:5000`

**Note**: The RAG system will initialize automatically on the first request. This may take a few moments as it loads the embedding model and builds the vector store.

### Frontend (Next.js)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

**Note**: The chat interface will automatically connect to the RAG system. Make sure the backend is running first.

## API Endpoints

The Flask backend provides the following endpoints:

### **Core Endpoints**
- `GET /` - Home endpoint
- `GET /api/health` - Health check endpoint
- `GET /api/data` - Sample data endpoint

### **RAG System Endpoints**
- `POST /api/rag/chat` - Send chat messages
- `GET /api/rag/health` - RAG system health check
- `GET /api/rag/status` - RAG system status
- `GET /api/rag/history/<session_id>` - Get conversation history
- `GET /api/rag/export/<session_id>` - Export conversation
- `DELETE /api/rag/clear/<session_id>` - Clear conversation session
- `POST /api/rag/rebuild` - Rebuild knowledge base
- `POST /api/rag/cleanup` - Clean up inactive sessions

## Features

### **Core Features**
- **CORS Support**: The Flask backend is configured with CORS to allow requests from the Next.js frontend
- **TypeScript**: The frontend uses TypeScript for better type safety
- **Tailwind CSS**: Modern styling with Tailwind CSS
- **Environment Variables**: Both applications support environment variables
- **Hot Reload**: Both applications support hot reloading during development

### **Agentic RAG System**
- **Multi-Agent Architecture**: 5 specialized agents working together
  - Query Understanding Agent
  - Knowledge Retrieval Agent
  - Context Synthesis Agent
  - Response Generation Agent
  - Conversation Manager Agent
- **FAISS Vector Store**: Fast similarity search with local storage
- **Groq LLM Integration**: Fast and powerful language model
- **Conversation Memory**: Session-based conversation history
- **Real-time Status Updates**: Live agent status tracking in UI
- **Document Processing**: Support for JSON, CSV, TXT, and Markdown files
- **Conversation Export**: Download conversations in JSON or TXT format

### **Academic Management Focus**
- **Domain-Specific Knowledge**: Academic policies, procedures, and rules
- **Intelligent Query Handling**: Context-aware responses
- **Multi-format Knowledge Base**: Structured and unstructured data support
- **Conversational Interface**: Natural language interaction

## Development

### Backend Development

The Flask app includes:
- CORS configuration for cross-origin requests
- Environment variable support
- Advanced RAG system with multi-agent architecture
- FAISS vector store for document retrieval
- Groq LLM integration for response generation
- Conversation memory management
- Comprehensive API endpoints
- Error handling and logging

### Frontend Development

The Next.js app includes:
- TypeScript support
- Tailwind CSS for styling
- Real-time chat interface
- Agent status tracking
- Conversation export functionality
- Responsive design
- Error handling for API calls
- Session management

## Production Deployment

### Backend

For production deployment of the Flask app:

1. Set `FLASK_ENV=production` in your environment variables
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Frontend

For production deployment of the Next.js app:

1. Build the application:
   ```bash
   npm run build
   ```

2. Start the production server:
   ```bash
   npm start
   ```

## Troubleshooting

### CORS Issues

If you encounter CORS issues:
1. Ensure the Flask backend is running on port 5000
2. Check that the CORS configuration in `app.py` includes the correct frontend URL
3. Verify that both applications are running simultaneously

### Port Conflicts

If port 5000 is already in use:
1. Change the port in the backend `.env` file
2. Update the frontend API calls to use the new port
3. Update the CORS configuration in the backend

### RAG System Issues

If the RAG system is not working:
1. Ensure you have added your Groq API key to the `.env` file
2. Check that the knowledge base files exist in `backend/data/knowledge/`
3. Verify the embedding model is downloading correctly
4. Check the backend logs for initialization errors

### Performance Issues

If the system is slow:
1. The first request may take longer as the RAG system initializes
2. Ensure you have sufficient RAM for the embedding model
3. Consider reducing the chunk size in the configuration if memory is limited

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## License

This project is open source and available under the MIT License.
