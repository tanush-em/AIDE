#!/usr/bin/env python3
"""
Main entry point for the Academic AI Management System
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from app import create_app
from app.rag.knowledge_base import KnowledgeBaseManager
from app.rag.policy_manager import PolicyManager
from app.agents.orchestrator import AgentOrchestrator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'uploads',
        'uploads/resources',
        'data',
        'data/policies',
        'data/knowledge_base'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

def initialize_rag_system():
    """Initialize RAG system components"""
    try:
        logger.info("🔄 Initializing RAG system...")
        
        # Initialize policy manager
        policy_manager = PolicyManager()
        logger.info("✅ Policy Manager initialized")
        
        # Initialize knowledge base manager
        kb_manager = KnowledgeBaseManager()
        logger.info("✅ Knowledge Base Manager initialized")
        
        # Load static policy files
        policy_files = [
            'backend/policies/leave_policies.json',
            'backend/policies/attendance_policies.json', 
            'backend/policies/event_policies.json'
        ]
        
        for policy_file in policy_files:
            if os.path.exists(policy_file):
                policy_manager.load_policy_file(policy_file)
                logger.info(f"✅ Loaded policy file: {policy_file}")
            else:
                logger.warning(f"⚠️ Policy file not found: {policy_file}")
        
        logger.info("✅ RAG system initialization completed")
        return policy_manager, kb_manager
        
    except Exception as e:
        logger.error(f"❌ Error initializing RAG system: {e}")
        raise e

def initialize_agents():
    """Initialize AI agents"""
    try:
        logger.info("🔄 Initializing AI agents...")
        
        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator()
        logger.info("✅ Agent Orchestrator initialized")
        
        # Test agent health
        health_status = orchestrator.get_health_status()
        logger.info(f"✅ Agent health status: {health_status}")
        
        logger.info("✅ AI agents initialization completed")
        return orchestrator
        
    except Exception as e:
        logger.error(f"❌ Error initializing AI agents: {e}")
        raise e

def main():
    """Main application entry point"""
    try:
        logger.info("🚀 Starting Academic AI Management System...")
        
        # Create necessary directories
        create_directories()
        
        # Initialize RAG system
        policy_manager, kb_manager = initialize_rag_system()
        
        # Initialize AI agents
        orchestrator = initialize_agents()
        
        # Create Flask app
        app = create_app()
        
        # Store RAG components in app context
        app.policy_manager = policy_manager
        app.kb_manager = kb_manager
        app.orchestrator = orchestrator
        
        # Get configuration
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_ENV') == 'development'
        
        logger.info(f"✅ Application initialized successfully")
        logger.info(f"🌐 Server will start on http://{host}:{port}")
        logger.info(f"🔧 Debug mode: {debug}")
        
        # Start the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise e

if __name__ == '__main__':
    main()
