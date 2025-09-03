from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Annotated, Union
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from bson import ObjectId
import json

def utc_now():
    """Get current UTC datetime (replacement for deprecated datetime.utcnow())"""
    return datetime.now(timezone.utc)

class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic compatibility"""
    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: Any,
        _handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return {"type": "string"}

class User(BaseModel):
    """User model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    status: str = "active"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "role": "user",
                "status": "active"
            }
        }
    }

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
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class Conversation(BaseModel):
    """Conversation model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    session_id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    status: str = "active"  # active, archived, deleted
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class Analytics(BaseModel):
    """Analytics model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    event_type: str  # query, response, error, user_action
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    query: Optional[str] = None
    response: Optional[str] = None
    source: str = "rag"  # rag, mongodb, combined
    confidence: Optional[Union[float, str]] = None
    processing_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=utc_now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class QueryLog(BaseModel):
    """Query log model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    query: str
    query_type: str  # rag, mongodb, combined
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    response: Optional[str] = None
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    agents_used: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=utc_now)
    success: bool = True
    error_message: Optional[str] = None
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

# Helper functions for model conversion
def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """Convert Pydantic model to dictionary"""
    return json.loads(model.json(by_alias=True))

def dict_to_model(data: Dict[str, Any], model_class: type) -> BaseModel:
    """Convert dictionary to Pydantic model"""
    return model_class(**data)
