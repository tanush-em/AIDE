from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
import json

class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic compatibility"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class User(BaseModel):
    """User model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Document(BaseModel):
    """Document model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    content: str
    document_type: str  # e.g., "policy", "procedure", "guide", "report"
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    version: str = "1.0"
    status: str = "active"  # active, draft, archived
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Conversation(BaseModel):
    """Conversation model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    session_id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, archived, deleted
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Analytics(BaseModel):
    """Analytics model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    event_type: str  # query, response, error, user_action
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    query: Optional[str] = None
    response: Optional[str] = None
    source: str = "rag"  # rag, mongodb, combined
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class QueryLog(BaseModel):
    """Query log model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    query: str
    query_type: str  # rag, mongodb, combined
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    response: Optional[str] = None
    confidence: Optional[float] = None
    processing_time: float
    agents_used: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    error_message: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Helper functions for model conversion
def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """Convert Pydantic model to dictionary"""
    return json.loads(model.json(by_alias=True))

def dict_to_model(data: Dict[str, Any], model_class: type) -> BaseModel:
    """Convert dictionary to Pydantic model"""
    return model_class(**data)
