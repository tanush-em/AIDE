from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import asyncio
import uuid

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["http://localhost:3000", "http://localhost:5001"], supports_credentials=True)

# Import and register blueprints
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.rag import rag_bp
from api.mongodb import mongodb_bp

app.register_blueprint(rag_bp, url_prefix='/api/rag')
app.register_blueprint(mongodb_bp, url_prefix='/api/mongodb')

@app.route('/')
def home():
    return jsonify({"message": "Flask Backend API is running!"})

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Backend is running successfully"
    })

@app.route('/api/data')
def get_data():
    return jsonify({
        "data": [
            {"id": 1, "name": "Item 1", "description": "First item"},
            {"id": 2, "name": "Item 2", "description": "Second item"},
            {"id": 3, "name": "Item 3", "description": "Third item"}
        ]
    })

@app.route('/api/enhanced-chat', methods=['POST'])
def enhanced_chat():
    """Enhanced chat endpoint that uses intelligent query routing"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        session_id = data.get('session_id')
        user_id = data.get('user_id', 'default')
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Import the enhanced RAG service
        from rag.enhanced_rag_service import enhanced_rag_service
        
        # Run async processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Ensure enhanced RAG is initialized
            if not enhanced_rag_service.is_initialized:
                loop.run_until_complete(enhanced_rag_service.initialize())
            
            # Process the query with intelligent routing
            result = loop.run_until_complete(
                enhanced_rag_service.process_query(session_id, message, user_id)
            )
            
            return jsonify({
                'session_id': session_id,
                'response': result['response'],
                'confidence': result.get('confidence', 'medium'),
                'suggestions': result.get('suggestions', []),
                'route_type': result.get('route_type', 'unknown'),
                'data_source': result.get('data_source', 'unknown'),
                'processing_time': result.get('processing_time', 0),
                'query_analysis': result.get('query_analysis', {}),
                'enhanced_with_mongodb': result.get('enhanced_with_mongodb', False)
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
