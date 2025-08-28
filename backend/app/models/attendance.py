from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

class SessionType(str, Enum):
    LECTURE = "lecture"
    LAB = "lab"
    TUTORIAL = "tutorial"
    PRACTICAL = "practical"

class Attendance(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=20)
    course_code: str = Field(..., min_length=1, max_length=20)
    course_name: str = Field(..., min_length=1, max_length=100)
    date: datetime
    status: AttendanceStatus
    marked_by: str = Field(..., min_length=1, max_length=20)
    session_type: SessionType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AttendanceCreate(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=20)
    course_code: str = Field(..., min_length=1, max_length=20)
    course_name: str = Field(..., min_length=1, max_length=100)
    date: datetime
    status: AttendanceStatus
    session_type: SessionType

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    session_type: Optional[SessionType] = None

class AttendanceResponse(BaseModel):
    id: str
    student_id: str
    course_code: str
    course_name: str
    date: datetime
    status: AttendanceStatus
    marked_by: str
    session_type: SessionType
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AttendanceStats(BaseModel):
    total_sessions: int
    present_sessions: int
    absent_sessions: int
    late_sessions: int
    excused_sessions: int
    attendance_percentage: float
    course_code: str
    course_name: str

class BulkAttendanceCreate(BaseModel):
    course_code: str = Field(..., min_length=1, max_length=20)
    course_name: str = Field(..., min_length=1, max_length=100)
    date: datetime
    session_type: SessionType
    attendance_records: list[dict] = Field(..., min_items=1)
