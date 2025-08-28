from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class LeaveType(str, Enum):
    MEDICAL = "medical"
    PERSONAL = "personal"
    EMERGENCY = "emergency"
    PLANNED = "planned"

class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class LeaveRequest(BaseModel):
    request_id: str = Field(..., min_length=1, max_length=20)
    student_id: str = Field(..., min_length=1, max_length=20)
    start_date: datetime
    end_date: datetime
    reason: str = Field(..., min_length=10, max_length=500)
    leave_type: LeaveType
    status: LeaveStatus = LeaveStatus.PENDING
    supporting_documents: List[str] = Field(default_factory=list)
    faculty_remarks: Optional[str] = Field(None, max_length=500)
    reviewed_by: Optional[str] = Field(None, min_length=1, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LeaveRequestCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    reason: str = Field(..., min_length=10, max_length=500)
    leave_type: LeaveType
    supporting_documents: Optional[List[str]] = Field(default_factory=list)

class LeaveRequestUpdate(BaseModel):
    status: Optional[LeaveStatus] = None
    faculty_remarks: Optional[str] = Field(None, max_length=500)

class LeaveRequestResponse(BaseModel):
    id: str
    request_id: str
    student_id: str
    start_date: datetime
    end_date: datetime
    reason: str
    leave_type: LeaveType
    status: LeaveStatus
    supporting_documents: List[str]
    faculty_remarks: Optional[str]
    reviewed_by: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LeaveBalance(BaseModel):
    student_id: str
    leave_type: LeaveType
    total_allowed: int
    used_days: int
    remaining_days: int
    academic_year: str

class LeaveStats(BaseModel):
    total_requests: int
    pending_requests: int
    approved_requests: int
    rejected_requests: int
    average_processing_time: float  # in hours
