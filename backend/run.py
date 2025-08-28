#!/usr/bin/env python3
"""
Main entry point for the Academic AI Management System
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'logs',
        'uploads',
        'chroma_db',
        'policies',
        'data/auth',
        'data/notice'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

def initialize_system():
    """Initialize the academic management system"""
    try:
        logger.info("🚀 Starting Academic AI Management System...")
        
        # Create necessary directories
        create_directories()
        
        # Import and create Flask app
        from app import create_app
        app = create_app()
        
        # Initialize RAG components
        initialize_rag_system(app)
        
        logger.info("✅ System initialization completed successfully")
        return app
        
    except Exception as e:
        logger.error(f"❌ System initialization failed: {e}")
        raise

def initialize_rag_system(app):
    """Initialize RAG (Retrieval-Augmented Generation) system"""
    try:
        logger.info("🔍 Initializing RAG system...")
        
        # Import RAG components
        from app.rag import KnowledgeBaseManager, PolicyManager
        
        # Initialize knowledge base
        kb_manager = KnowledgeBaseManager()
        app.kb_manager = kb_manager
        
        # Initialize policy manager
        policy_manager = PolicyManager()
        app.policy_manager = policy_manager
        
        # Load static files into knowledge base
        asyncio.run(kb_manager.load_static_files())
        
        logger.info("✅ RAG system initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ RAG system initialization failed: {e}")
        # Continue without RAG if it fails
        pass

def main():
    """Main function to run the application"""
    try:
        # Initialize the system
        app = initialize_system()
        
        # Get configuration
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5001))
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        logger.info(f"🔧 Debug mode: {debug}")
        
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
