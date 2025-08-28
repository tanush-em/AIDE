from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    TECHNICAL = "technical"
    CULTURAL = "cultural"
    SPORTS = "sports"
    ACADEMIC = "academic"
    WORKSHOP = "workshop"
    SEMINAR = "seminar"

class EventStatus(str, Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RegistrationStatus(str, Enum):
    REGISTERED = "registered"
    ATTENDED = "attended"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"

class Event(BaseModel):
    event_id: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    event_type: EventType
    start_datetime: datetime
    end_datetime: datetime
    location: str = Field(..., min_length=1, max_length=200)
    max_participants: int = Field(..., ge=1)
    current_registrations: int = Field(default=0, ge=0)
    registration_deadline: datetime
    created_by: str = Field(..., min_length=1, max_length=20)
    requirements: List[str] = Field(default_factory=list)
    status: EventStatus = EventStatus.UPCOMING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    event_type: EventType
    start_datetime: datetime
    end_datetime: datetime
    location: str = Field(..., min_length=1, max_length=200)
    max_participants: int = Field(..., ge=1)
    registration_deadline: datetime
    requirements: Optional[List[str]] = Field(default_factory=list)

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    event_type: Optional[EventType] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    max_participants: Optional[int] = Field(None, ge=1)
    registration_deadline: Optional[datetime] = None
    requirements: Optional[List[str]] = None
    status: Optional[EventStatus] = None

class EventResponse(BaseModel):
    id: str
    event_id: str
    title: str
    description: str
    event_type: EventType
    start_datetime: datetime
    end_datetime: datetime
    location: str
    max_participants: int
    current_registrations: int
    registration_deadline: datetime
    created_by: str
    requirements: List[str]
    status: EventStatus
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EventRegistration(BaseModel):
    registration_id: str = Field(..., min_length=1, max_length=20)
    event_id: str = Field(..., min_length=1, max_length=20)
    student_id: str = Field(..., min_length=1, max_length=20)
    registration_data: Dict[str, Any] = Field(default_factory=dict)
    status: RegistrationStatus = RegistrationStatus.REGISTERED
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EventRegistrationCreate(BaseModel):
    event_id: str = Field(..., min_length=1, max_length=20)
    registration_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class EventRegistrationUpdate(BaseModel):
    status: Optional[RegistrationStatus] = None
    registration_data: Optional[Dict[str, Any]] = None

class EventRegistrationResponse(BaseModel):
    id: str
    registration_id: str
    event_id: str
    student_id: str
    registration_data: Dict[str, Any]
    status: RegistrationStatus
    registered_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EventStats(BaseModel):
    total_events: int
    upcoming_events: int
    ongoing_events: int
    completed_events: int
    total_registrations: int
    average_registration_rate: float
