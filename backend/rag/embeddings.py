from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np

class EmbeddingManager:
    """Manages text embeddings for the RAG system"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text"""
        if isinstance(text, str):
            text = [text]
        
        embeddings = self.model.encode(text, convert_to_numpy=True)
        return embeddings
    
    def embed_single_text(self, text: str) -> List[float]:
        """Generate embedding for a single text and return as a flat list"""
        embedding = self.embed_text(text)
        # Ensure we return a flat list, not nested lists
        if isinstance(embedding, np.ndarray):
            if embedding.ndim == 2:
                return embedding[0].tolist()  # Extract the first embedding and convert to list
            elif embedding.ndim == 1:
                return embedding.tolist()  # Already 1D, just convert to list
        elif isinstance(embedding, list):
            # If it's already a list, return the first element if it's nested
            if len(embedding) > 0 and isinstance(embedding[0], list):
                return embedding[0]
            return embedding
        return embedding.tolist()[0] if hasattr(embedding, 'tolist') else embedding
    
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """Generate embeddings for multiple documents"""
        return self.embed_text(documents)
    
    def compute_similarity(self, query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and documents"""
        # Normalize embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        
        # Compute cosine similarity
        similarities = np.dot(doc_norms, query_norm)
        return similarities
    
    def get_model_info(self) -> dict:
        """Get information about the embedding model"""
        return {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'max_sequence_length': self.model.max_seq_length
        }
