import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from rag.rag_service import RAGService

def utc_now():
    """Get current UTC datetime (replacement for deprecated datetime.utcnow())"""
    return datetime.now(timezone.utc)

logger = logging.getLogger(__name__)

class EnhancedRAGService:
    """Enhanced RAG service that uses only file-based data sources"""
    
    def __init__(self):
        self.rag_service = RAGService()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize RAG service with file-based data sources"""
        try:
            # Initialize RAG service
            await self.rag_service.initialize()
            
            self.is_initialized = True
            logger.info("Enhanced RAG service initialized successfully with file-based data sources!")
            print("Enhanced RAG service initialized successfully with file-based data sources!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced RAG service: {str(e)}")
            print(f"Failed to initialize Enhanced RAG service: {str(e)}")
            self.is_initialized = False
            raise e
    
    async def process_query(self, session_id: str, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a query using file-based RAG system
        
        Args:
            session_id: Session identifier
            query: User query
            user_id: Optional user identifier
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Process query using RAG service
            rag_result = await self.rag_service.process_query(session_id, query, user_id)
            
            # Enhance result with additional metadata
            enhanced_result = {
                "success": True,
                "response": rag_result.get("response", ""),
                "confidence": rag_result.get("confidence", "medium"),
                "suggestions": rag_result.get("suggestions", []),
                "data_source": "file_based",
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": utc_now().isoformat(),
                "processing_time": rag_result.get("processing_time", 0),
                "file_metadata": {
                    "source": "knowledge_files",
                    "total_documents": rag_result.get("total_documents", 0),
                    "retrieved_chunks": len(rag_result.get("search_results", []))
                }
            }
            
            # Log analytics
            await self._log_analytics(enhanced_result, query, user_id)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "response": f"I encountered an error while processing your request: {str(e)}",
                "confidence": "low",
                "suggestions": ["Please try rephrasing your question", "Check if the knowledge base contains relevant information"],
                "data_source": "file_based",
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": utc_now().isoformat(),
                "error": str(e)
            }
    
    async def _log_analytics(self, result: Dict[str, Any], query: str, user_id: Optional[str]):
        """Log query analytics for monitoring"""
        try:
            analytics_data = {
                "query": query,
                "user_id": user_id,
                "success": result.get("success", False),
                "confidence": result.get("confidence", "unknown"),
                "data_source": result.get("data_source", "file_based"),
                "processing_time": result.get("processing_time", 0),
                "timestamp": utc_now(),
                "file_metadata": result.get("file_metadata", {})
            }
            
            # For now, just log to console - can be enhanced with file-based logging
            logger.info(f"Query analytics: {analytics_data}")
            
        except Exception as e:
            logger.error(f"Error logging analytics: {str(e)}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            if not self.is_initialized:
                return {
                    "status": "not_initialized",
                    "message": "System not initialized"
                }
            
            # Get RAG system status
            rag_status = {
                "status": "initialized" if self.rag_service.is_initialized else "not_initialized",
                "vector_store_documents": self.rag_service.vector_store.get_document_count() if self.rag_service.vector_store else 0,
                "embedding_model": "loaded" if self.rag_service.embedding_manager else "not_loaded"
            }
            
            return {
                "overall_status": "healthy" if self.is_initialized else "unhealthy",
                "rag_system": rag_status,
                "data_sources": {
                    "type": "file_based",
                    "knowledge_base_path": "data/knowledge",
                    "supported_formats": [".txt", ".json", ".csv", ".md", ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"]
                },
                "timestamp": utc_now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": utc_now().isoformat()
            }
    
    async def close(self):
        """Close the service and cleanup resources"""
        try:
            if self.rag_service:
                # Close any resources if needed
                pass
            
            self.is_initialized = False
            logger.info("Enhanced RAG service closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing Enhanced RAG service: {str(e)}")

# Global instance
enhanced_rag_service = EnhancedRAGService()