from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

# Setup logging
from utils.logging_config import setup_logging, get_logger, log_request_info, log_response_info, log_error

# Initialize logging
setup_logging()

# Get logger for this module
logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5001"], supports_credentials=True)

# Request logging middleware
@app.before_request
def log_request():
    """Log all incoming requests"""
    log_request_info(request, logger)

@app.after_request
def log_response(response):
    """Log all outgoing responses"""
    log_response_info(response, logger)
    return response

# Error handling middleware
@app.errorhandler(404)
def not_found(error):
    log_error(error, logger, "404 Not Found")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    log_error(error, logger, "500 Internal Server Error")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    log_error(error, logger, "Unhandled Exception")
    return jsonify({'error': str(error)}), 500

# Import and register blueprints
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.rag import rag_bp
from api.task_workflow import task_workflow_bp

app.register_blueprint(rag_bp, url_prefix='/api/rag')
app.register_blueprint(task_workflow_bp, url_prefix='/api/tasks')

@app.route('/')
def home():
    logger.info("Home endpoint accessed")
    print("Home endpoint accessed")
    return jsonify({"message": "Flask Backend API is running!"})

@app.route('/api/health')
def health_check():
    logger.info("Health check endpoint accessed")
    print("Health check endpoint accessed")
    return jsonify({
        "status": "healthy",
        "message": "Backend is running successfully",
        "endpoints": {
            "chat": "/api/rag/chat",
            "task_chat": "/api/tasks/chat",
            "task_chat_stream": "/api/tasks/chat/stream",
            "health": "/api/rag/health",
            "task_health": "/api/tasks/health"
        }
    })

@app.route('/api/data')
def get_data():
    logger.info("Data endpoint accessed")
    print("Data endpoint accessed")
    return jsonify({
        "data": [
            {"id": 1, "name": "Item 1", "description": "First item"},
            {"id": 2, "name": "Item 2", "description": "Second item"},
            {"id": 3, "name": "Item 3", "description": "Third item"}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Flask backend on port {port}")
    logger.info(f"Debug mode: {debug}")
    print(f"Starting Flask backend on port {port}")
    print(f"Debug mode: {debug}")
    print("ChromaDB integration is active!")
    print("Vector store will be initialized at: data/vector_store")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
