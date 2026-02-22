Cats vs Dogs – End-to-End MLOps Pipeline
Group Number: 48
JAISINGHANI ANJALI – 2024aa05370

JOKARE MAHESH SHIVANAND – 2024aa05366

MOHAMED ASHIK M Z – 2024aa05144

SHA ABDUL KHUDUS – 2024aa05754

VIDHI MITTAL – 2024aa05684
Project Overview
This project demonstrates a complete end-to-end MLOps pipeline for a binary image classification task (Cats vs Dogs).
The objective was not just to train a model, but to build a structured and reproducible workflow that covers the full lifecycle of a machine learning system — from data handling and model training to deployment, testing, and monitoring.
The pipeline includes:
Data preprocessing and model training
Reproducible experiments using DVC
A containerized FastAPI inference service
CI/CD integration with GitHub Actions
Monitoring using Prometheus and Grafana
Post-deployment validation and smoke testing
The focus of this assignment is production-readiness and reproducibility.
Dataset
Source: Kaggle – Dogs vs Cats
https://www.kaggle.com/datasets/salader/dogs-vs-cats
Dataset details:
25,000 RGB images
Binary classification: Cat vs Dog
Images resized to 224x224
Data split:
80% Training
10% Validation
10% Testing
Data augmentation applied to improve generalization
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
Model Details
Model Architecture: Improved CNN

Classes: 2 (Cat, Dog)

Input Size: 224x224 RGB

Model Size: 29.4 MB

Training Device: CPU
Performance Metrics
Overall Accuracy: 80.00%

Cat Accuracy: 82.00%

Dog Accuracy: 78.00%
Training Configuration
Epochs: 25

Learning Rate: 0.0001

Batch Size: 16

Weight Decay: 1e-05
All training settings are controlled using config.json.
Reproducible Training with DVC
The project uses DVC to make the training pipeline reproducible.
To execute the pipeline:
dvc repro
This will run the defined stages and generate the trained model at:
models/best_model.pth
You can also train directly using:
python src/training/train.py --config config.json
Running the Inference Service
To build and start the full system locally:
docker-compose up --build
Once running, the following services are available:
API: http://localhost:8000
Swagger UI: http://localhost:8000/docs
Prometheus: http://localhost:9090
Grafana: http://localhost:3000
MLflow: http://localhost:5000
API Endpoints
Health Check:
curl http://localhost:8000/health
Prediction:
curl -X POST -F "file=@test_image_smoke.jpg" http://localhost:8000/predict
The API accepts an image file and returns the predicted class (Cat or Dog).
Testing
The project includes both unit tests and smoke tests.
Run unit tests:
pytest
Run smoke tests:
python smoke_tests.py
These ensure the API is working correctly and the model returns valid predictions.
Monitoring
Monitoring configuration is available inside the monitoring/ directory.
The system integrates:
Prometheus for metrics collection
Grafana for visualization
model_monitor.py for checking model performance after deployment
This ensures the service can be validated even after deployment.
Summary
This project demonstrates a structured and reproducible MLOps workflow for a real-world image classification task. It integrates training, tracking, deployment, monitoring, and testing into a single cohesive pipeline.
The focus was on building something closer to a production-ready system rather than just training a model.
 