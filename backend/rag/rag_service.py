import os
import sys
import time
from typing import Dict, Any, Optional, List
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import RAGConfig
from utils.memory import MemoryManager
from rag.embeddings import EmbeddingManager
from rag.vector_store import ChromaDBVectorStore
from rag.document_loader import DocumentLoader
from agents.orchestrator import RAGOrchestrator
from agents.query_agent import QueryUnderstandingAgent
from agents.retrieval_agent import KnowledgeRetrievalAgent
from agents.synthesis_agent import ContextSynthesisAgent
from agents.generation_agent import ResponseGenerationAgent
from agents.conversation_agent import ConversationManagerAgent

# Setup logging
logger = logging.getLogger(__name__)

class RAGService:
    """Main service class that manages the entire RAG system"""
    
    def __init__(self):
        self.config = RAGConfig()
        self.config.validate()
        
        # Initialize components
        self.embedding_manager = None
        self.vector_store = None
        self.memory_manager = None
        self.orchestrator = None
        self.conversation_agent = None
        
        # System status
        self.is_initialized = False
        self.initialization_error = None
    
    async def initialize(self):
        """Initialize the RAG system"""
        try:
            logger.info("Initializing RAG system...")
            print("Initializing RAG system...")
            
            # Initialize embedding manager
            logger.info("Loading embedding model...")
            print("Loading embedding model...")
            self.embedding_manager = EmbeddingManager(self.config.EMBEDDING_MODEL)
            
            # Initialize vector store
            logger.info("Initializing vector store...")
            print("Initializing vector store...")
            self.vector_store = ChromaDBVectorStore(
                self.config.VECTOR_STORE_PATH,
                self.embedding_manager,
                self.config.CHROMADB_COLLECTION_NAME
            )
            
            # Initialize memory manager
            logger.info("Initializing memory manager...")
            print("Initializing memory manager...")
            self.memory_manager = MemoryManager()
            
            # Initialize agents
            logger.info("Initializing agents...")
            print("Initializing agents...")
            self._initialize_agents()
            
            # Initialize orchestrator
            logger.info("Initializing orchestrator...")
            print("Initializing orchestrator...")
            self.orchestrator = RAGOrchestrator(
                query_agent=self.query_agent,
                retrieval_agent=self.retrieval_agent,
                synthesis_agent=self.synthesis_agent,
                generation_agent=self.generation_agent,
                conversation_agent=self.conversation_agent
            )
            
            # Set orchestrator in conversation agent
            self.conversation_agent.orchestrator = self.orchestrator
            
            # Always rebuild vector store on startup to ensure latest knowledge base files are indexed
            logger.info("Rebuilding vector store from knowledge base on startup...")
            print("Rebuilding vector store from knowledge base on startup...")
            await self._rebuild_vector_store()
            
            self.is_initialized = True
            logger.info("RAG system initialized successfully!")
            print("RAG system initialized successfully!")
            
        except Exception as e:
            self.initialization_error = str(e)
            logger.error(f"Error initializing RAG system: {e}")
            print(f"Error initializing RAG system: {e}")
            raise
    
    def _initialize_agents(self):
        """Initialize all RAG agents"""
        self.query_agent = QueryUnderstandingAgent()
        self.retrieval_agent = KnowledgeRetrievalAgent(self.vector_store)
        self.synthesis_agent = ContextSynthesisAgent()
        self.generation_agent = ResponseGenerationAgent(
            api_key=self.config.GROQ_API_KEY,
            model_name=self.config.LLM_MODEL
        )
        self.conversation_agent = ConversationManagerAgent(self.memory_manager)
    
    async def _build_vector_store(self):
        """Build the vector store from knowledge base"""
        try:
            # Load documents
            loader = DocumentLoader(self.config.KNOWLEDGE_BASE_PATH)
            documents = loader.load_all_documents()
            
            if documents:
                # Add documents to vector store
                self.vector_store.add_documents(
                    documents,
                    chunk_size=self.config.CHUNK_SIZE,
                    chunk_overlap=self.config.CHUNK_OVERLAP
                )
                logger.info(f"Vector store built with {len(documents)} documents")
                print(f"Vector store built with {len(documents)} documents")
            else:
                logger.warning("No documents found in knowledge base")
                print("No documents found in knowledge base")
                
        except Exception as e:
            logger.error(f"Error building vector store: {e}")
            print(f"Error building vector store: {e}")
            raise
    
    async def _rebuild_vector_store(self):
        """Rebuild the vector store from knowledge base (clears existing data)"""
        try:
            # Rebuild the entire vector store
            self.vector_store.rebuild_index(self.config.KNOWLEDGE_BASE_PATH)
            document_count = self.vector_store.get_document_count()
            logger.info(f"Vector store rebuilt with {document_count} document chunks")
            print(f"Vector store rebuilt with {document_count} document chunks")
                
        except Exception as e:
            logger.error(f"Error rebuilding vector store: {e}")
            print(f"Error rebuilding vector store: {e}")
            raise
    
    async def process_query(self, session_id: str, message: str, user_id: str = "default", uploaded_documents: List[str] = None) -> Dict[str, Any]:
        """Process a user query through the RAG system"""
        if not self.is_initialized:
            raise RuntimeError("RAG system not initialized")
        
        try:
            # Process through conversation agent
            result = await self.conversation_agent.process({
                'session_id': session_id,
                'message': message,
                'user_id': user_id,
                'uploaded_documents': uploaded_documents or []
            })
            
            return result
            
        except Exception as e:
            return {
                'session_id': session_id,
                'response': f"I encountered an error: {str(e)}. Please try again.",
                'confidence': 'low',
                'suggestions': ['Try rephrasing your question'],
                'error': str(e)
            }
    
    async def rebuild_knowledge_base(self) -> Dict[str, Any]:
        """Rebuild the knowledge base and vector store"""
        if not self.is_initialized:
            raise RuntimeError("RAG system not initialized")
        
        try:
            logger.info("Rebuilding knowledge base...")
            print("Rebuilding knowledge base...")
            self.vector_store.rebuild_index(self.config.KNOWLEDGE_BASE_PATH)
            
            return {
                'status': 'success',
                'message': 'Knowledge base rebuilt successfully',
                'document_count': self.vector_store.get_document_count()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error rebuilding knowledge base: {str(e)}',
                'error': str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the status of the RAG system"""
        status = {
            'initialized': self.is_initialized,
            'initialization_error': self.initialization_error,
            'config': {
                'embedding_model': self.config.EMBEDDING_MODEL,
                'llm_model': self.config.LLM_MODEL,
                'knowledge_base_path': self.config.KNOWLEDGE_BASE_PATH,
                'vector_store_path': self.config.VECTOR_STORE_PATH
            }
        }
        
        if self.is_initialized:
            status.update({
                'vector_store': self.vector_store.get_statistics(),
                'memory_manager': self.memory_manager.get_sessions_info(),
                'orchestrator': self.orchestrator.get_system_health() if self.orchestrator else None
            })
        
        return status
    
    def get_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """Get conversation history for a session"""
        if not self.is_initialized:
            return {'error': 'RAG system not initialized'}
        
        try:
            session = self.memory_manager.get_session(session_id)
            return {
                'session_id': session_id,
                'history': session.get_conversation_history(),
                'session_info': self.conversation_agent.get_session_info(session_id)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def export_conversation(self, session_id: str, format_type: str = 'json') -> Dict[str, Any]:
        """Export a conversation session"""
        if not self.is_initialized:
            return {'error': 'RAG system not initialized'}
        
        try:
            exported_data = self.conversation_agent.export_conversation(session_id, format_type)
            return {
                'session_id': session_id,
                'format': format_type,
                'data': exported_data
            }
        except Exception as e:
            return {'error': str(e)}
    
    def clear_session(self, session_id: str) -> Dict[str, Any]:
        """Clear a conversation session"""
        if not self.is_initialized:
            return {'error': 'RAG system not initialized'}
        
        try:
            success = self.conversation_agent.clear_session(session_id)
            return {
                'session_id': session_id,
                'cleared': success,
                'message': 'Session cleared successfully' if success else 'Session not found'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup_inactive_sessions(self, timeout: int = None) -> Dict[str, Any]:
        """Clean up inactive sessions"""
        if not self.is_initialized:
            return {'error': 'RAG system not initialized'}
        
        try:
            timeout = timeout or self.config.SESSION_TIMEOUT
            self.conversation_agent.cleanup_inactive_sessions(timeout)
            
            return {
                'status': 'success',
                'message': f'Cleaned up sessions inactive for {timeout} seconds',
                'active_sessions': len(self.memory_manager.get_all_sessions())
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def upload_document(self, file_path: str, session_id: str, filename: str) -> Dict[str, Any]:
        """Upload and process a document for the current session"""
        if not self.is_initialized:
            raise RuntimeError("RAG system not initialized")
        
        try:
            # Load the document
            loader = DocumentLoader(os.path.dirname(file_path))
            document = loader.load_document(os.path.basename(file_path))
            
            # Generate unique document ID
            document_id = f"uploaded_{session_id}_{filename}_{int(time.time())}"
            
            # Add session and priority metadata
            document['metadata'].update({
                'session_id': session_id,
                'document_id': document_id,
                'upload_priority': 'high',  # High priority for uploaded documents
                'upload_timestamp': time.time(),
                'source_type': 'uploaded'
            })
            
            # Add to vector store with high priority
            self.vector_store.add_documents(
                [document],
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP
            )
            
            # Store document info in memory manager for session tracking
            if hasattr(self.memory_manager, 'add_uploaded_document'):
                self.memory_manager.add_uploaded_document(session_id, document_id, filename)
            
            logger.info(f"Document {filename} uploaded and processed successfully")
            
            return {
                'document_id': document_id,
                'filename': filename,
                'session_id': session_id,
                'chunks_created': len(document.get('content', '').split('\n')),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error uploading document {filename}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'filename': filename
            }
    
    async def remove_uploaded_document(self, document_id: str) -> Dict[str, Any]:
        """Remove an uploaded document from the vector store"""
        if not self.is_initialized:
            raise RuntimeError("RAG system not initialized")
        
        try:
            # Remove document from vector store
            # Note: This is a simplified approach. In production, you'd want to track document IDs more precisely
            success = self.vector_store.delete_documents_by_metadata('document_id', document_id)
            
            if success:
                logger.info(f"Document {document_id} removed successfully")
                return {
                    'success': True,
                    'document_id': document_id,
                    'chunks_removed': 1  # This would need to be tracked more precisely
                }
            else:
                return {
                    'success': False,
                    'error': 'Document not found or could not be removed'
                }
                
        except Exception as e:
            logger.error(f"Error removing document {document_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_uploaded_documents(self, session_id: str) -> Dict[str, Any]:
        """Get list of uploaded documents for a session"""
        if not self.is_initialized:
            raise RuntimeError("RAG system not initialized")
        
        try:
            # Get documents from vector store with session metadata
            documents = self.vector_store.get_documents_by_metadata('session_id', session_id)
            
            # Filter for uploaded documents only
            uploaded_docs = [
                doc for doc in documents 
                if doc.get('metadata', {}).get('source_type') == 'uploaded'
            ]
            
            return {
                'session_id': session_id,
                'documents': uploaded_docs,
                'count': len(uploaded_docs)
            }
            
        except Exception as e:
            logger.error(f"Error getting uploaded documents for session {session_id}: {e}")
            return {
                'session_id': session_id,
                'documents': [],
                'count': 0,
                'error': str(e)
            }
