from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class NoticePriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class NoticeCategory(str, Enum):
    ACADEMIC = "academic"
    ADMINISTRATIVE = "administrative"
    EVENT = "event"
    GENERAL = "general"
    EMERGENCY = "emergency"

class Notice(BaseModel):
    notice_id: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10, max_length=2000)
    priority: NoticePriority
    category: NoticeCategory
    target_audience: List[str] = Field(..., min_items=1)
    department: str = Field(..., min_length=1, max_length=100)
    posted_by: str = Field(..., min_length=1, max_length=20)
    attachments: List[str] = Field(default_factory=list)
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NoticeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10, max_length=2000)
    priority: NoticePriority
    category: NoticeCategory
    target_audience: List[str] = Field(..., min_items=1)
    department: str = Field(..., min_length=1, max_length=100)
    attachments: Optional[List[str]] = Field(default_factory=list)
    expiry_date: Optional[datetime] = None

class NoticeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=2000)
    priority: Optional[NoticePriority] = None
    category: Optional[NoticeCategory] = None
    target_audience: Optional[List[str]] = Field(None, min_items=1)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    attachments: Optional[List[str]] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class NoticeResponse(BaseModel):
    id: str
    notice_id: str
    title: str
    content: str
    priority: NoticePriority
    category: NoticeCategory
    target_audience: List[str]
    department: str
    posted_by: str
    attachments: List[str]
    expiry_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NoticeStats(BaseModel):
    total_notices: int
    active_notices: int
    high_priority_notices: int
    academic_notices: int
    administrative_notices: int
    event_notices: int
