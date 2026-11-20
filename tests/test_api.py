from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app, students, attendance_records
import app.main as main_module

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_data():
    students.clear()
    attendance_records.clear()
    main_module._next_student_id = 1
    yield
    students.clear()
    attendance_records.clear()
    main_module._next_student_id = 1


def create_sample_student():
    response = client.post(
        "/students",
        json={
            "name": "Asha Rao",
            "roll_number": "CT001",
            "department": "Computer Science",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_root_and_health():
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "healthy"}


def test_create_and_list_student():
    create_sample_student()
    response = client.get("/students")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_duplicate_roll_number_rejected():
    create_sample_student()
    response = client.post(
        "/students",
        json={
            "name": "Another Student",
            "roll_number": "CT001",
            "department": "AI",
        },
    )
    assert response.status_code == 409


def test_search_student_by_roll_number():
    create_sample_student()
    response = client.get("/students/roll/CT001")
    assert response.status_code == 200
    assert response.json()["name"] == "Asha Rao"


def test_unknown_roll_number_returns_404():
    assert client.get("/students/roll/UNKNOWN").status_code == 404


def test_record_and_retrieve_attendance():
    student = create_sample_student()
    response = client.post(
        "/attendance",
        json={
            "student_id": student["id"],
            "attendance_date": date.today().isoformat(),
            "status": "present",
        },
    )
    assert response.status_code == 201
    records = client.get(f"/attendance/{student['id']}")
    assert len(records.json()) == 1


def test_duplicate_attendance_rejected():
    student = create_sample_student()
    payload = {
        "student_id": student["id"],
        "attendance_date": date.today().isoformat(),
        "status": "present",
    }
    assert client.post("/attendance", json=payload).status_code == 201
    assert client.post("/attendance", json=payload).status_code == 409


def test_attendance_percentage():
    student = create_sample_student()
    for status in ("present", "absent", "present"):
        response = client.post(
            "/attendance",
            json={
                "student_id": student["id"],
                "attendance_date": date.today().isoformat()
                if not attendance_records
                else date.fromordinal(date.today().toordinal() + len(attendance_records)).isoformat(),
                "status": status,
            },
        )
        assert response.status_code == 201

    result = client.get(f"/students/{student['id']}/percentage").json()
    assert result["total_classes"] == 3
    assert result["attendance_percentage"] == pytest.approx(66.67)


def test_attendance_for_unknown_student():
    assert client.get("/attendance/999").status_code == 404
