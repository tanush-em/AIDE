import os
from dotenv import load_dotenv

load_dotenv()

class RAGConfig:
    """Configuration settings for the RAG system"""
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Model Settings
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "llama3.1-8b-8192"  # Groq model (updated from deprecated llama3-8b-8192)
    
    # Vector Store Settings
    VECTOR_STORE_PATH = "data/vector_store"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # ChromaDB Settings
    CHROMADB_COLLECTION_NAME = "documents"
    CHROMADB_PERSIST_DIRECTORY = "data/vector_store"
    CHROMADB_DISTANCE_METRIC = "cosine"
    
    # Memory Settings
    MAX_CONVERSATION_HISTORY = 10
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # Knowledge Base Settings
    KNOWLEDGE_BASE_PATH = "data/knowledge"
    SUPPORTED_FORMATS = ['.txt', '.json', '.csv', '.md']
    
    # Agent Settings
    MAX_RETRIEVAL_RESULTS = 5
    SIMILARITY_THRESHOLD = 0.7
    
    # Response Settings
    MAX_RESPONSE_LENGTH = 1000
    TEMPERATURE = 0.7
    
    # Server Settings
    DEFAULT_PORT = 5001
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        # Make GROQ_API_KEY optional - system will use fallback if not provided
        if not cls.GROQ_API_KEY:
            print("WARNING: GROQ_API_KEY not found in environment variables. System will use fallback responses.")
        
        if not os.path.exists(cls.KNOWLEDGE_BASE_PATH):
            raise ValueError(f"Knowledge base path does not exist: {cls.KNOWLEDGE_BASE_PATH}")
        
        return True
