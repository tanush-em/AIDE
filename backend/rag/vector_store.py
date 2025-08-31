import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Tuple
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .embeddings import EmbeddingManager
from .document_loader import DocumentLoader

class FAISSVectorStore:
    """FAISS-based vector store for document storage and retrieval"""
    
    def __init__(self, store_path: str, embedding_manager: EmbeddingManager):
        self.store_path = Path(store_path)
        self.embedding_manager = embedding_manager
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Create directory if it doesn't exist
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and documents"""
        index_path = self.store_path / "faiss_index"
        docs_path = self.store_path / "documents.pkl"
        metadata_path = self.store_path / "metadata.pkl"
        
        if index_path.exists() and docs_path.exists() and metadata_path.exists():
            try:
                self.index = faiss.read_index(str(index_path))
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                print(f"Loaded existing index with {len(self.documents)} documents")
            except Exception as e:
                print(f"Error loading existing index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        dimension = self.embedding_manager.dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.documents = []
        self.metadata = []
        print("Created new FAISS index")
    
    def _save_index(self):
        """Save FAISS index and documents"""
        index_path = self.store_path / "faiss_index"
        docs_path = self.store_path / "documents.pkl"
        metadata_path = self.store_path / "metadata.pkl"
        
        faiss.write_index(self.index, str(index_path))
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def add_documents(self, documents: List[Dict[str, Any]], chunk_size: int = 1000, chunk_overlap: int = 200):
        """Add documents to the vector store with chunking"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        for doc in documents:
            # Split document into chunks
            chunks = text_splitter.split_text(doc['content'])
            
            for i, chunk in enumerate(chunks):
                # Generate embedding for chunk
                embedding = self.embedding_manager.embed_text(chunk)
                
                # Add to FAISS index
                self.index.add(embedding)
                
                # Store document chunk and metadata
                self.documents.append(chunk)
                self.metadata.append({
                    'source': doc['source'],
                    'title': doc['title'],
                    'category': doc['category'],
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'original_metadata': doc['metadata']
                })
        
        # Save the updated index
        self._save_index()
        print(f"Added {len(documents)} documents to vector store")
    
    def similarity_search(self, query: str, k: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embedding_manager.embed_text(query)
        
        # Search in FAISS index
        similarities, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(self.documents) and similarity >= threshold:
                results.append({
                    'content': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'similarity_score': float(similarity),
                    'rank': i + 1
                })
        
        return results
    
    def get_document_count(self) -> int:
        """Get the number of documents in the store"""
        return len(self.documents)
    
    def rebuild_index(self, knowledge_base_path: str):
        """Rebuild the entire index from knowledge base"""
        print("Rebuilding vector store index...")
        
        # Clear existing index
        self._create_new_index()
        
        # Load documents
        loader = DocumentLoader(knowledge_base_path)
        documents = loader.load_all_documents()
        
        if documents:
            # Add documents to index
            self.add_documents(documents)
            print(f"Rebuilt index with {len(documents)} documents")
        else:
            print("No documents found in knowledge base")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal if self.index else 0,
            'embedding_dimension': self.embedding_manager.dimension,
            'store_path': str(self.store_path)
        }
