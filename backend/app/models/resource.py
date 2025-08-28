from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ResourceType(str, Enum):
    NOTES = "notes"
    SLIDES = "slides"
    VIDEO = "video"
    ASSIGNMENT = "assignment"
    REFERENCE = "reference"
    SYLLABUS = "syllabus"
    QUESTION_PAPER = "question_paper"

class AccessLevel(str, Enum):
    PUBLIC = "public"
    COURSE_SPECIFIC = "course_specific"
    DEPARTMENT_SPECIFIC = "department_specific"
    FACULTY_ONLY = "faculty_only"

class Resource(BaseModel):
    resource_id: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=500)
    course_code: Optional[str] = Field(None, min_length=1, max_length=20)
    resource_type: ResourceType
    file_url: str = Field(..., min_length=1)
    file_size: int = Field(..., ge=0)  # in bytes
    uploaded_by: str = Field(..., min_length=1, max_length=20)
    tags: List[str] = Field(default_factory=list)
    access_level: AccessLevel
    download_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ResourceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=500)
    course_code: Optional[str] = Field(None, min_length=1, max_length=20)
    resource_type: ResourceType
    file_url: str = Field(..., min_length=1)
    file_size: int = Field(..., ge=0)
    tags: Optional[List[str]] = Field(default_factory=list)
    access_level: AccessLevel

class ResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    course_code: Optional[str] = Field(None, min_length=1, max_length=20)
    resource_type: Optional[ResourceType] = None
    file_url: Optional[str] = Field(None, min_length=1)
    file_size: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    access_level: Optional[AccessLevel] = None

class ResourceResponse(BaseModel):
    id: str
    resource_id: str
    title: str
    description: str
    course_code: Optional[str]
    resource_type: ResourceType
    file_url: str
    file_size: int
    uploaded_by: str
    tags: List[str]
    access_level: AccessLevel
    download_count: int
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ResourceStats(BaseModel):
    total_resources: int
    total_downloads: int
    resources_by_type: dict
    most_downloaded_resources: List[dict]
    average_file_size: float
