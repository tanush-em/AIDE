import chromadb
from sentence_transformers import SentenceTransformer
import json
import pandas as pd
from typing import List, Dict, Any, Optional
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the knowledge base manager with ChromaDB"""
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self.collections = {}
            
            # Initialize collections
            self.collections['policies'] = self.client.get_or_create_collection(
                name="policies",
                metadata={"description": "Academic policies and rules"}
            )
            self.collections['faqs'] = self.client.get_or_create_collection(
                name="faqs", 
                metadata={"description": "Frequently asked questions"}
            )
            self.collections['notices'] = self.client.get_or_create_collection(
                name="notices",
                metadata={"description": "Academic notices and announcements"}
            )
            
            logger.info("✅ Knowledge base initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize knowledge base: {e}")
            raise
    
    async def load_static_files(self, policies_dir: str = "./policies"):
        """Load and embed static policy files"""
        try:
            if not os.path.exists(policies_dir):
                logger.warning(f"Policies directory {policies_dir} does not exist")
                return
            
            for filename in os.listdir(policies_dir):
                file_path = os.path.join(policies_dir, filename)
                if filename.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        await self.embed_policy_data(filename, data)
                elif filename.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    await self.embed_csv_data(filename, df)
                    
            logger.info(f"✅ Loaded static files from {policies_dir}")
            
        except Exception as e:
            logger.error(f"❌ Error loading static files: {e}")
            raise
    
    async def embed_policy_data(self, source: str, data: Dict[str, Any]):
        """Embed policy data into vector store"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            def extract_text_recursively(obj, prefix=""):
                texts = []
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, (dict, list)):
                            texts.extend(extract_text_recursively(value, f"{prefix}.{key}"))
                        else:
                            texts.append(f"{prefix}.{key}: {value}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        texts.extend(extract_text_recursively(item, f"{prefix}[{i}]"))
                else:
                    texts.append(f"{prefix}: {obj}")
                return texts
            
            text_chunks = extract_text_recursively(data)
            
            for i, chunk in enumerate(text_chunks):
                documents.append(chunk)
                metadatas.append({
                    "source": source,
                    "chunk_id": i,
                    "type": "policy",
                    "timestamp": datetime.utcnow().isoformat()
                })
                ids.append(f"{source}_{i}")
            
            if documents:
                embeddings = self.encoder.encode(documents).tolist()
                self.collections['policies'].add(
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"✅ Embedded {len(documents)} chunks from {source}")
                
        except Exception as e:
            logger.error(f"❌ Error embedding policy data: {e}")
            raise
    
    async def embed_csv_data(self, source: str, df: pd.DataFrame):
        """Embed CSV data into vector store"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for index, row in df.iterrows():
                # Convert row to text representation
                text = " ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                documents.append(text)
                metadatas.append({
                    "source": source,
                    "row_id": index,
                    "type": "data",
                    "timestamp": datetime.utcnow().isoformat()
                })
                ids.append(f"{source}_{index}")
            
            if documents:
                embeddings = self.encoder.encode(documents).tolist()
                self.collections['policies'].add(
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"✅ Embedded {len(documents)} rows from {source}")
                
        except Exception as e:
            logger.error(f"❌ Error embedding CSV data: {e}")
            raise
    
    async def semantic_search(self, query: str, collection_name: str = "policies", 
                            n_results: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Perform semantic search in knowledge base"""
        try:
            query_embedding = self.encoder.encode([query]).tolist()[0]
            
            # Prepare where clause for filtering
            where_clause = None
            if filter_metadata:
                where_clause = filter_metadata
            
            results = self.collections[collection_name].query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=['documents', 'metadatas', 'distances']
            )
            
            return [
                {
                    "document": doc,
                    "metadata": meta,
                    "similarity": 1 - dist,  # Convert distance to similarity
                    "source": meta.get("source", "unknown")
                }
                for doc, meta, dist in zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                )
            ]
            
        except Exception as e:
            logger.error(f"❌ Error in semantic search: {e}")
            return []
    
    async def add_document(self, collection_name: str, document: str, metadata: Dict[str, Any], doc_id: str):
        """Add a single document to the knowledge base"""
        try:
            embedding = self.encoder.encode([document]).tolist()[0]
            self.collections[collection_name].add(
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.info(f"✅ Added document {doc_id} to {collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Error adding document: {e}")
            raise
    
    async def update_document(self, collection_name: str, doc_id: str, document: str, metadata: Dict[str, Any]):
        """Update an existing document in the knowledge base"""
        try:
            embedding = self.encoder.encode([document]).tolist()[0]
            self.collections[collection_name].update(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata]
            )
            logger.info(f"✅ Updated document {doc_id} in {collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Error updating document: {e}")
            raise
    
    async def delete_document(self, collection_name: str, doc_id: str):
        """Delete a document from the knowledge base"""
        try:
            self.collections[collection_name].delete(ids=[doc_id])
            logger.info(f"✅ Deleted document {doc_id} from {collection_name}")
            
        except Exception as e:
            logger.error(f"❌ Error deleting document: {e}")
            raise
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics about a collection"""
        try:
            collection = self.collections[collection_name]
            count = collection.count()
            return {
                "collection_name": collection_name,
                "document_count": count,
                "metadata": collection.metadata
            }
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {e}")
            return {}
    
    def get_all_collections_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        stats = {}
        for collection_name in self.collections:
            stats[collection_name] = self.get_collection_stats(collection_name)
        return stats
