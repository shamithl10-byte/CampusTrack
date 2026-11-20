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

## Docker
```bash
docker build -t campustrack-api:1.0 .
docker run --rm -p 8000:8000 campustrack-api:1.0
```

## Ansible
Run from the repository root on a Linux environment with Ansible installed:
```bash
ansible-playbook -i ansible/inventory.ini ansible/site.yml --ask-become-pass
```
The role creates an application configuration directory and renders its
environment configuration using a Jinja2 template.

## Kubernetes with Minikube
Build the image in Minikube's image store:
```bash
minikube image build -t campustrack-api:1.0 .
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl get deployments,pods,services
kubectl scale deployment campustrack --replicas=5
kubectl scale deployment campustrack --replicas=3
```
The NodePort service uses port 30080. The deployment starts with three
replicas and defines HTTP readiness and liveness probes on `/health`.
