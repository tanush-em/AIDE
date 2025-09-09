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
import asyncio
import threading

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.rag import rag_bp, init_rag_service, ensure_rag_initialized
from api.task_workflow import task_workflow_bp
from api.attendance import attendance_bp
from api.leave_management import leave_bp
from api.notice_board import notice_bp
from api.dashboard import dashboard_bp
from api.student_management import student_bp
from api.data_export import export_bp
from api.question_paper import question_paper_bp
from api.resources import resources_bp
from api.placements import placements_bp

app.register_blueprint(rag_bp, url_prefix='/api/rag')
app.register_blueprint(task_workflow_bp, url_prefix='/api/tasks')
app.register_blueprint(attendance_bp)
app.register_blueprint(leave_bp)
app.register_blueprint(notice_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(student_bp)
app.register_blueprint(export_bp)
app.register_blueprint(question_paper_bp)
app.register_blueprint(resources_bp)
app.register_blueprint(placements_bp)

def auto_reindex_vector_store():
    """Automatically reindex the vector store on startup"""
    def run_reindex():
        try:
            logger.info("Starting automatic vector store reindexing...")
            print("🔄 Starting automatic vector store reindexing...")
            
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Initialize RAG service
                init_rag_service()
                
                # Ensure RAG is initialized
                loop.run_until_complete(ensure_rag_initialized())
                
                # Import the rag module to access the global rag_service
                import api.rag as rag_module
                
                if rag_module.rag_service and rag_module.rag_service.is_initialized:
                    # Rebuild the knowledge base
                    result = loop.run_until_complete(rag_module.rag_service.rebuild_knowledge_base())
                    
                    if result.get('status') == 'success':
                        logger.info(f"✅ Vector store reindexed successfully with {result.get('document_count', 0)} documents")
                        print(f"✅ Vector store reindexed successfully with {result.get('document_count', 0)} documents")
                    else:
                        logger.warning(f"⚠️ Vector store reindexing completed with warnings: {result.get('message', 'Unknown error')}")
                        print(f"⚠️ Vector store reindexing completed with warnings: {result.get('message', 'Unknown error')}")
                else:
                    logger.warning("⚠️ RAG service not initialized, skipping auto-reindex")
                    print("⚠️ RAG service not initialized, skipping auto-reindex")
                    
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"❌ Error during automatic vector store reindexing: {e}")
            print(f"❌ Error during automatic vector store reindexing: {e}")
    
    # Run reindexing in a separate thread to avoid blocking Flask startup
    reindex_thread = threading.Thread(target=run_reindex, daemon=True)
    reindex_thread.start()
    logger.info("🚀 Auto-reindex thread started")
    print("🚀 Auto-reindex thread started")

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
        "features": {
            "auto_reindex": "Vector store automatically reindexes on startup",
            "manual_reindex": "Reindex button available in chat interface"
        },
        "endpoints": {
            "chat": "/api/rag/chat",
            "task_chat": "/api/tasks/chat",
            "task_chat_stream": "/api/tasks/chat/stream",
            "health": "/api/rag/health",
            "task_health": "/api/tasks/health",
            "reindex": "/api/rag/rebuild",
            "attendance": "/api/attendance/students",
            "leave_management": "/api/leave/requests",
            "notice_board": "/api/notices",
            "dashboard": "/api/dashboard/stats",
            "students": "/api/students",
            "courses": "/api/courses",
            "export": "/api/export",
            "question_paper": "/api/question-paper",
            "resources": "/api/resources",
            "placements": "/api/placements"
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
    
    # Start automatic vector store reindexing
    auto_reindex_vector_store()
    
    app.run(host='0.0.0.0', port=port, debug=debug)
