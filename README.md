# CampusTrack – Student Attendance Management API

CampusTrack is a REST API for student registration and attendance tracking.
It is built with Python, FastAPI and Uvicorn.

## Features
- Register and list students
- Search students by roll number
- Record and retrieve attendance
- Calculate attendance percentage
- Health endpoint for deployment probes

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for Swagger documentation.

## Tests
```bash
pytest -v
```

Student and attendance data are held in memory and reset when the process
restarts. This project does not claim persistent database storage.

## Repository
https://github.com/shamithl10-byte/CampusTrack

## Continuous integration
The Jenkinsfile defines a Pipeline job that checks out the configured SCM,
installs Python dependencies, runs pytest, publishes JUnit XML results and
archives selected project files. SCM polling is configured at a two-minute
interval using `H/2 * * * *`. Jenkins must be configured with this repository
as its Pipeline-from-SCM source for polling to operate.
