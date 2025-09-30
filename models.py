from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Student(SQLModel, table=True):
    """Student model for database table"""
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    age: int
    grade: str  # e.g., "A", "B", "C", etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

class StudentCreate(SQLModel):
    """Model for creating a new student"""
    first_name: str
    last_name: str
    email: str
    age: int
    grade: str

class StudentUpdate(SQLModel):
    """Model for updating student information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None
    is_active: Optional[bool] = None

class StudentResponse(SQLModel):
    """Model for API response"""
    id: int
    first_name: str
    last_name: str
    email: str
    age: int
    grade: str
    created_at: datetime
    is_active: bool