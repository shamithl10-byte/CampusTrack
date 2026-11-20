from datetime import date
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="CampusTrack Student Attendance API",
    description="API for student registration and attendance tracking",
    version="1.0.0",
)

students: dict[int, dict] = {}
attendance_records: list[dict] = []
_next_student_id = 1


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    roll_number: str = Field(min_length=1, max_length=30)
    department: str = Field(min_length=1, max_length=100)


class AttendanceCreate(BaseModel):
    student_id: int
    attendance_date: date = Field(default_factory=date.today)
    status: Literal["present", "absent"]


@app.get("/")
def root():
    return {
        "message": "Welcome to CampusTrack Student Attendance API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    global _next_student_id

    if any(s["roll_number"] == student.roll_number for s in students.values()):
        raise HTTPException(status_code=409, detail="Roll number already exists")

    record = student.model_dump()
    record["id"] = _next_student_id
    students[_next_student_id] = record
    _next_student_id += 1
    return record


@app.get("/students")
def list_students():
    return list(students.values())


@app.post("/attendance", status_code=201)
def record_attendance(entry: AttendanceCreate):
    if entry.student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    duplicate = any(
        r["student_id"] == entry.student_id
        and r["attendance_date"] == entry.attendance_date
        for r in attendance_records
    )
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Attendance already recorded for this date",
        )

    record = entry.model_dump()
    record["attendance_date"] = record["attendance_date"].isoformat()
    attendance_records.append(record)
    return record


@app.get("/attendance/{student_id}")
def get_attendance(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return [r for r in attendance_records if r["student_id"] == student_id]


@app.get("/students/{student_id}/percentage")
def attendance_percentage(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")

    records = [r for r in attendance_records if r["student_id"] == student_id]
    if not records:
        percentage = 0.0
    else:
        present = sum(r["status"] == "present" for r in records)
        percentage = round(present * 100 / len(records), 2)

    return {
        "student_id": student_id,
        "total_classes": len(records),
        "present": sum(r["status"] == "present" for r in records),
        "attendance_percentage": percentage,
    }
