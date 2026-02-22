Cats vs Dogs – End-to-End MLOps Pipeline

Group Number: 48

JAISINGHANI ANJALI – 2024aa05370
JOKARE MAHESH SHIVANAND – 2024aa05366
MOHAMED ASHIK M Z – 2024aa05144
SHA ABDUL KHUDUS – 2024aa05754
VIDHI MITTAL – 2024aa05684

Project Overview

This project demonstrates a complete end-to-end MLOps pipeline for a binary image classification task (Cats vs Dogs).
The objective was not just to train a model, but to build a reproducible, automated, and production-ready ML workflow covering:

Data preprocessing and versioning

Model training and experiment tracking

Containerized inference service

CI/CD automation using GitHub Actions

Automated deployment

Monitoring with Prometheus & Grafana

Post-deployment smoke testing

This project focuses on reproducibility, automation, and production-readiness, aligning with real-world ML system design.

Dataset

Source: Kaggle – Dogs vs Cats
https://www.kaggle.com/datasets/salader/dogs-vs-cats

Dataset Details:

25,000 RGB images
Binary classification: Cat vs Dog
Images resized to 224x224
Train/Validation/Test split:
80% Training
10% Validation
10% Testing

Data augmentation applied for better generalization

The dataset is tracked using DVC to ensure reproducibility of the pipeline.

Project Structure

MLOPS ASSIGNMENT 2
│
├── .github/workflows/ci-cd.yml     # CI/CD workflow
├── data/                           # Dataset (tracked with DVC)
├── models/
│   └── best_model.pth              # Trained model
├── src/
│   ├── data/                       # Data preprocessing logic
│   ├── models/                     # CNN architecture
│   ├── training/                   # Training pipeline
│   └── inference/                  # FastAPI inference service
├── tests/                          # Unit tests
├── monitoring/                     # Prometheus & Grafana config
├── docker-compose.yml              # Multi-service deployment
├── Dockerfile                      # Container definition
├── requirements.txt
├── requirements-docker.txt
├── smoke_tests.py                  # API smoke tests
├── model_monitor.py                # Model performance checks
├── config.json                     # Training configuration
└── dvc.yaml                        # Reproducible pipeline definition

Model Architecture

Model Type: Improved CNN
Classes: 2 (Cat, Dog)
Input Size: 224x224 RGB
Model Size: ~29 MB
Training Device: CPU

Performance Metrics

Overall Accuracy: 80.00%
Cat Accuracy: 82.00%
Dog Accuracy: 78.00%

Training Configuration

Controlled using config.json:
Epochs: 25
Learning Rate: 0.0001
Batch Size: 16
Weight Decay: 1e-05

eproducible Training with DVC

This project uses DVC to make the training pipeline reproducible.

Run full pipeline:
dvc repro

This generates:

models/best_model.pth
Or train manually:
python src/training/train.py --config config.json

 Running the Inference Service (Local Deployment)

To start the full system locally:

docker-compose up -d

Services Available:
Service	URL
API	http://localhost:8000

Swagger UI	http://localhost:8000/docs

Prometheus	http://localhost:9090

Grafana	http://localhost:3000

MLflow	http://localhost:5000

API Endpoints
Health Check
curl http://localhost:8000/health
Prediction
curl -X POST -F "file=@test_image_smoke.jpg" \
http://localhost:8000/predict

The API accepts an image file and returns:

Predicted class (Cat/Dog)

Probability score

Testing

Run Unit Tests
pytest

Run Smoke Tests
python smoke_tests.py

Smoke tests validate:

/health endpoint

/predict endpoint

If these fail during CI/CD, the pipeline fails automatically.


CI/CD Pipeline (GitHub Actions)

A fully automated CI/CD pipeline is implemented using GitHub Actions.

The pipeline runs on every push to the main branch.

Stage 1 — Continuous Integration

Checkout repository
Setup Python environment
Install dependencies
Run unit tests using pytest

Stage 2 — Build & Publish Docker Image

Build Docker image using Dockerfile
Login securely to Docker Hub using GitHub Secrets

Push image to Docker Hub:

docker.io/abdulbits/cats-dogs-mlops:latest

Stage 3 — Continuous Deployment

Pull latest Docker image
Start container using docker run
Wait for API startup

Run smoke tests:

Health check (/health)
Prediction test (/predict)

If smoke tests fail, the pipeline fails automatically.
This demonstrates a full CI/CD automation workflow.

Deployment Strategy

Two deployment strategies are implemented:

1️) Automated Deployment (CI/CD)

The GitHub Actions pipeline:

Pulls image from Docker Hub
Deploys container automatically
Runs smoke tests

2️) Local Deployment (Docker Compose)

Docker Compose runs:

FastAPI inference service
Prometheus metrics server
Grafana dashboard
MLflow tracking server
This satisfies the assignment requirement of deployment using Docker Compose.

Monitoring & Logging

Monitoring is configured inside the monitoring/ directory.

The system integrates:
Prometheus → Metrics collection
Grafana → Visualization dashboard
model_monitor.py → Post-deployment performance validation
The FastAPI service:
Logs requests and responses (excluding sensitive data)
Exposes Prometheus metrics:
Request count
Latency metrics

This ensures visibility and observability after deployment.

