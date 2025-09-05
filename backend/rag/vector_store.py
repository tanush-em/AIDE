import chromadb
import numpy as np
import os
import sys
from typing import List, Dict, Any, Tuple
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.embeddings import EmbeddingManager
from rag.document_loader import DocumentLoader

logger = logging.getLogger(__name__)

class ChromaDBVectorStore:
    """ChromaDB-based vector store for document storage and retrieval"""
    
    def __init__(self, store_path: str, embedding_manager: EmbeddingManager, collection_name: str = "documents"):
        self.store_path = Path(store_path)
        self.embedding_manager = embedding_manager
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        # Create directory if it doesn't exist
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client and collection
        self._initialize_chromadb()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB client with persistent storage
            self.client = chromadb.PersistentClient(path=str(self.store_path))
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Loaded existing ChromaDB collection: {self.collection_name}")
            except Exception:
                # Create new collection if it doesn't exist
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                )
                logger.info(f"Created new ChromaDB collection: {self.collection_name}")
            
            logger.info(f"ChromaDB initialized successfully at {self.store_path}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]], chunk_size: int = 1000, chunk_overlap: int = 200):
        """Add documents to the vector store with chunking"""
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
            )
            
            all_chunks = []
            all_embeddings = []
            all_metadatas = []
            all_ids = []
            
            chunk_counter = 0
            
            for doc in documents:
                # Split document into chunks
                chunks = text_splitter.split_text(doc['content'])
                
                for i, chunk in enumerate(chunks):
                    # Generate embedding for chunk
                    embedding = self.embedding_manager.embed_single_text(chunk)
                    
                    # Prepare metadata - ChromaDB only accepts str, int, float, bool, or None
                    original_meta = doc.get('metadata', {})
                    metadata = {
                        'source': str(doc.get('source', 'unknown')),
                        'title': str(doc.get('title', 'Untitled')),
                        'category': str(doc.get('category', 'general')),
                        'chunk_index': int(i),
                        'total_chunks': int(len(chunks)),
                        'chunk_size': int(len(chunk)),
                        'document_type': str(doc.get('document_type', 'text'))
                    }
                    
                    # Add flattened original metadata as separate fields
                    if isinstance(original_meta, dict):
                        for key, value in original_meta.items():
                            if isinstance(value, (str, int, float, bool)) or value is None:
                                metadata[f'meta_{key}'] = value
                            else:
                                metadata[f'meta_{key}'] = str(value)
                    
                    # Generate unique ID for the chunk
                    chunk_id = f"chunk_{chunk_counter}_{doc.get('source', 'unknown')}_{i}"
                    
                    all_chunks.append(chunk)
                    all_embeddings.append(embedding)
                    all_metadatas.append(metadata)
                    all_ids.append(chunk_id)
                    
                    chunk_counter += 1
            
            if all_chunks:
                # Ensure embeddings are in the correct format for ChromaDB
                # ChromaDB expects embeddings to be a list of lists, where each inner list is an embedding
                formatted_embeddings = []
                for embedding in all_embeddings:
                    if isinstance(embedding, list):
                        # If it's already a list of floats, use it as is
                        if len(embedding) > 0 and isinstance(embedding[0], (int, float)):
                            formatted_embeddings.append(embedding)
                        else:
                            # If it's nested, flatten it
                            flattened = []
                            for item in embedding:
                                if isinstance(item, list):
                                    flattened.extend(item)
                                else:
                                    flattened.append(item)
                            formatted_embeddings.append([float(x) for x in flattened])
                    else:
                        # If it's not a list, convert it to the expected format
                        formatted_embeddings.append([float(x) for x in embedding])
                
                # Add all chunks to ChromaDB collection
                self.collection.add(
                    documents=all_chunks,
                    embeddings=formatted_embeddings,
                    metadatas=all_metadatas,
                    ids=all_ids
                )
                
                logger.info(f"Added {len(all_chunks)} document chunks to ChromaDB collection")
            else:
                logger.warning("No document chunks to add")
                
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents using ChromaDB"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_manager.embed_single_text(query)
            
            # Ensure query embedding is in the right format for ChromaDB (list of lists)
            # ChromaDB expects query_embeddings to be a list of lists, where each inner list is an embedding
            if isinstance(query_embedding, list):
                # Check if it's already properly formatted
                if len(query_embedding) > 0 and isinstance(query_embedding[0], (int, float)):
                    # It's a flat list of floats, wrap it in another list
                    query_embedding = [query_embedding]
                elif len(query_embedding) > 0 and isinstance(query_embedding[0], list):
                    # It's already a list of lists, use as is
                    pass
                else:
                    # Flatten and wrap
                    flattened = []
                    for item in query_embedding:
                        if isinstance(item, list):
                            flattened.extend(item)
                        else:
                            flattened.append(item)
                    query_embedding = [[float(x) for x in flattened]]
            else:
                # If it's not a list, convert it to the expected format
                query_embedding = [[float(x) for x in query_embedding]]
            
            # Search in ChromaDB collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process results
            processed_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    # Cosine distance = 1 - cosine_similarity, so similarity = 1 - distance
                    similarity_score = 1 - distance
                    
                    if similarity_score >= threshold:
                        processed_results.append({
                            'content': doc,
                            'metadata': metadata,
                            'similarity_score': float(similarity_score),
                            'rank': i + 1
                        })
            
            logger.info(f"ChromaDB search returned {len(processed_results)} results above threshold {threshold}")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in ChromaDB similarity search: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get the number of documents in the store"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    def rebuild_index(self, knowledge_base_path: str):
        """Rebuild the entire index from knowledge base"""
        try:
            logger.info("Rebuilding ChromaDB vector store index...")
            
            # Clear existing collection
            self.client.delete_collection(name=self.collection_name)
            
            # Recreate collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Load documents
            loader = DocumentLoader(knowledge_base_path)
            documents = loader.load_all_documents()
            
            if documents:
                # Add documents to index
                self.add_documents(documents)
                logger.info(f"Rebuilt ChromaDB index with {len(documents)} documents")
            else:
                logger.warning("No documents found in knowledge base")
                
        except Exception as e:
            logger.error(f"Error rebuilding ChromaDB index: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            return {
                'total_documents': self.get_document_count(),
                'collection_name': self.collection_name,
                'embedding_dimension': self.embedding_manager.dimension,
                'store_path': str(self.store_path),
                'chromadb_version': chromadb.__version__
            }
        except Exception as e:
            logger.error(f"Error getting ChromaDB statistics: {e}")
            return {
                'error': str(e),
                'store_path': str(self.store_path)
            }
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete specific documents from the store"""
        try:
            self.collection.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents from ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents from ChromaDB: {e}")
            return False
    
    def update_document(self, document_id: str, new_content: str, new_metadata: Dict[str, Any]) -> bool:
        """Update a specific document in the store"""
        try:
            # Generate new embedding
            new_embedding = self.embedding_manager.embed_single_text(new_content)
            
            # Update the document
            self.collection.update(
                ids=[document_id],
                documents=[new_content],
                embeddings=new_embedding,
                metadatas=[new_metadata]
            )
            
            logger.info(f"Updated document {document_id} in ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document {document_id} in ChromaDB: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get detailed information about the ChromaDB collection"""
        try:
            return {
                'name': self.collection.name,
                'count': self.collection.count(),
                'metadata': self.collection.metadata,
                'embedding_function': str(self.collection.embedding_function) if hasattr(self.collection, 'embedding_function') else 'custom'
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {'error': str(e)}

# For backward compatibility, create an alias
FAISSVectorStore = ChromaDBVectorStore
