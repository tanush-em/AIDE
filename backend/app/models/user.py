from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    COORDINATOR = "coordinator"

class UserProfile(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    department: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    
    # Student-specific fields
    year: Optional[int] = Field(None, ge=1, le=5)
    batch: Optional[str] = Field(None, max_length=20)
    
    # Faculty-specific fields
    employee_id: Optional[str] = Field(None, max_length=20)
    designation: Optional[str] = Field(None, max_length=100)

class User(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    password_hash: str = Field(..., min_length=1)
    role: UserRole
    profile: UserProfile
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole
    profile: UserProfile

class UserUpdate(BaseModel):
    profile: Optional[UserProfile] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    user_id: str
    email: str
    role: UserRole
    profile: UserProfile
    is_active: bool
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
    role: UserRole

class LoginResponse(BaseModel):
    success: bool
    user: UserResponse
    access_token: str
    refresh_token: str
