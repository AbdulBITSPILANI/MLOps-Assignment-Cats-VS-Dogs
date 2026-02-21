#!/usr/bin/env python3
"""
Verification script to ensure all required MLOps files are present and accessible
"""

import os
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if file exists and print status"""
    path = Path(file_path)
    exists = path.exists() and path.is_file()
    size = path.stat().st_size if exists else 0
    status = "✅ EXISTS" if exists else "❌ MISSING"
    print(f"{status} {description}: {file_path} ({size} bytes)")
    return exists

def check_dir_exists(dir_path, description):
    """Check if directory exists and print status"""
    path = Path(dir_path)
    exists = path.exists() and path.is_dir()
    status = "✅ EXISTS" if exists else "❌ MISSING"
    print(f"{status} {description}: {dir_path}")
    return exists

def main():
    """Verify all required MLOps files"""
    print("🔍 MLOps Assignment File Verification")
    print("=" * 60)
    
    # Critical files that evaluators look for
    critical_files = [
        ("Dockerfile", "Dockerfile (M2 Requirement)"),
        ("requirements.txt", "Requirements file (M2 Requirement)"),
        ("dvc.yaml", "DVC pipeline file (M1 Requirement)"),
        ("smoke_tests.py", "Smoke test script (M4 Requirement)"),
        (".github/workflows/ci-cd.yml", "CI/CD pipeline (M3 Requirement)"),
        ("post_deployment_eval.py", "Post-deployment evaluation (M5 Requirement)"),
    ]
    
    # Check critical files
    print("\n🔴 CRITICAL FILES:")
    all_critical_exist = True
    for file_path, description in critical_files:
        if not check_file_exists(file_path, description):
            all_critical_exist = False
    
    # Check directories
    critical_dirs = [
        (".dvc", "DVC configuration directory"),
        ("src", "Source code directory"),
        ("models", "Model artifacts directory"),
        ("mlruns", "MLflow tracking directory"),
        ("tests", "Unit tests directory"),
        ("k8s", "Kubernetes manifests"),
        ("monitoring", "Monitoring configuration"),
    ]
    
    print("\n📁 CRITICAL DIRECTORIES:")
    for dir_path, description in critical_dirs:
        if not check_dir_exists(dir_path, description):
            all_critical_exist = False
    
    # Check model artifacts
    print("\n🎯 MODEL ARTIFACTS:")
    model_files = [
        ("models/best_model.pth", "Trained model file"),
        ("model_performance.json", "Performance metrics"),
    ]
    
    for file_path, description in model_files:
        check_file_exists(file_path, description)
    
    # Check source code structure
    print("\n📝 SOURCE CODE STRUCTURE:")
    source_files = [
        ("src/training/train.py", "Training script"),
        ("src/models/cnn_model.py", "Model definition"),
        ("src/inference/app.py", "Inference service"),
        ("src/data/preprocessing.py", "Data preprocessing"),
    ]
    
    for file_path, description in source_files:
        check_file_exists(file_path, description)
    
    # Check test files
    print("\n🧪 TEST FILES:")
    test_files = [
        ("tests/test_preprocessing.py", "Preprocessing tests"),
        ("tests/test_model.py", "Model tests"),
        ("tests/test_inference.py", "Inference tests"),
    ]
    
    for file_path, description in test_files:
        check_file_exists(file_path, description)
    
    # Summary
    print("\n" + "=" * 60)
    if all_critical_exist:
        print("🎉 ALL CRITICAL FILES PRESENT!")
        print("✅ Ready for high-score submission")
    else:
        print("❌ CRITICAL FILES MISSING!")
        print("🚨 Fix missing files before submission")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
