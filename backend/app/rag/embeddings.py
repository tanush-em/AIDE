from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize embedding manager with specified model"""
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            logger.info(f"✅ Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def encode_text(self, text: str) -> List[float]:
        """Encode a single text into embeddings"""
        try:
            embedding = self.model.encode([text])
            return embedding[0].tolist()
        except Exception as e:
            logger.error(f"❌ Error encoding text: {e}")
            raise
    
    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts into embeddings"""
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"❌ Error encoding texts: {e}")
            raise
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        try:
            embedding1 = self.encode_text(text1)
            embedding2 = self.encode_text(text2)
            
            # Convert to numpy arrays for similarity calculation
            emb1 = np.array(embedding1).reshape(1, -1)
            emb2 = np.array(embedding2).reshape(1, -1)
            
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query: str, candidates: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find most similar texts to a query"""
        try:
            if not candidates:
                return []
            
            # Encode query and candidates
            query_embedding = self.encode_text(query)
            candidate_embeddings = self.encode_texts(candidates)
            
            # Calculate similarities
            similarities = []
            for i, candidate_embedding in enumerate(candidate_embeddings):
                similarity = cosine_similarity(
                    np.array(query_embedding).reshape(1, -1),
                    np.array(candidate_embedding).reshape(1, -1)
                )[0][0]
                similarities.append({
                    'text': candidates[i],
                    'similarity': float(similarity),
                    'index': i
                })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error finding most similar: {e}")
            return []
    
    def batch_similarity_search(self, queries: List[str], documents: List[str], 
                              threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Perform batch similarity search"""
        try:
            if not queries or not documents:
                return []
            
            # Encode all queries and documents
            query_embeddings = self.encode_texts(queries)
            document_embeddings = self.encode_texts(documents)
            
            results = []
            
            for i, query_embedding in enumerate(query_embeddings):
                query_results = []
                for j, doc_embedding in enumerate(document_embeddings):
                    similarity = cosine_similarity(
                        np.array(query_embedding).reshape(1, -1),
                        np.array(doc_embedding).reshape(1, -1)
                    )[0][0]
                    
                    if similarity >= threshold:
                        query_results.append({
                            'document': documents[j],
                            'similarity': float(similarity),
                            'document_index': j
                        })
                
                # Sort by similarity
                query_results.sort(key=lambda x: x['similarity'], reverse=True)
                
                results.append({
                    'query': queries[i],
                    'query_index': i,
                    'matches': query_results
                })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in batch similarity search: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        try:
            # Create a dummy embedding to get the dimension
            dummy_embedding = self.encode_text("test")
            return len(dummy_embedding)
        except Exception as e:
            logger.error(f"❌ Error getting embedding dimension: {e}")
            return 0
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.get_embedding_dimension(),
            'max_sequence_length': self.model.max_seq_length if hasattr(self.model, 'max_seq_length') else None
        }
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better embedding quality"""
        try:
            # Basic text preprocessing
            text = text.strip()
            text = text.lower()
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Error preprocessing text: {e}")
            return text
    
    def encode_with_preprocessing(self, text: str) -> List[float]:
        """Encode text with preprocessing"""
        processed_text = self.preprocess_text(text)
        return self.encode_text(processed_text)
    
    def encode_texts_with_preprocessing(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts with preprocessing"""
        processed_texts = [self.preprocess_text(text) for text in texts]
        return self.encode_texts(processed_texts)
