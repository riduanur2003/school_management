from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from database import engine, create_db_and_tables, get_session
from models import Student, StudentCreate, StudentUpdate, StudentResponse

# Create FastAPI app
app = FastAPI(
    title="Student Registration API",
    description="A simple API for student registration using FastAPI and SQLModel",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    """Create database tables on startup"""
    create_db_and_tables()

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Student Registration API"}

@app.post("/students/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, session: Session = Depends(get_session)):
    """Create a new student"""
    # Check if email already exists
    existing_student = session.exec(
        select(Student).where(Student.email == student.email)
    ).first()
    
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create student instance
    db_student = Student(**student.dict())
    
    # Add to database
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    
    return db_student

@app.get("/students/", response_model=List[StudentResponse])
def read_students(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """Get all students with pagination"""
    statement = select(Student).offset(skip).limit(limit)
    students = session.exec(statement).all()
    return students

@app.get("/students/{student_id}", response_model=StudentResponse)
def read_student(student_id: int, session: Session = Depends(get_session)):
    """Get a specific student by ID"""
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student

@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_update: StudentUpdate, session: Session = Depends(get_session)):
    """Update a student's information"""
    db_student = session.get(Student, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Update only provided fields
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)
    
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    
    return db_student

@app.delete("/students/{student_id}")
def delete_student(student_id: int, session: Session = Depends(get_session)):
    """Delete a student (soft delete by setting is_active=False)"""
    db_student = session.get(Student, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Soft delete
    db_student.is_active = False
    session.add(db_student)
    session.commit()
    
    return {"message": "Student deleted successfully"}

@app.get("/students/email/{email}", response_model=StudentResponse)
def read_student_by_email(email: str, session: Session = Depends(get_session)):
    """Get a student by email"""
    statement = select(Student).where(Student.email == email)
    student = session.exec(statement).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student

@app.get("/students/active/", response_model=List[StudentResponse])
def read_active_students(session: Session = Depends(get_session)):
    """Get all active students"""
    statement = select(Student).where(Student.is_active == True)
    students = session.exec(statement).all()
    return students

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)