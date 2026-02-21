#!/usr/bin/env python3
"""
Prepare MLOps assignment ZIP file with all required deliverables
"""

import os
import zipfile
from pathlib import Path
import shutil

def create_assignment_zip():
    """Create comprehensive ZIP file for MLOps assignment submission"""
    
    # Define project root
    project_root = Path(".")
    zip_name = "MLOps_Assignment_Complete.zip"
    
    # Files and directories to include
    include_items = [
        # Core source code
        "src/",
        
        # Configuration files
        "Dockerfile",
        "docker-compose.yml", 
        "requirements.txt",
        "requirements-docker.txt",
        "config.json",
        "params.yaml",
        
        # MLOps configuration
        "dvc.yaml",
        "dvc.lock",
        ".dvc/",
        ".dvcignore",
        
        # CI/CD
        ".github/",
        
        # Kubernetes
        "k8s/",
        
        # Monitoring
        "monitoring/",
        
        # Model artifacts
        "models/",
        "model_performance.json",
        
        # Testing
        "tests/",
        "pytest.ini",
        "smoke_tests.py",
        "post_deployment_eval.py",
        "verify_files.py",
        
        # Data (processed only, exclude raw large datasets)
        "data/processed/",
        "data/.gitignore",
        
        # Documentation
        "README.md",
        "CRITICAL_ISSUES_FIXED.md",
        "FINAL_RESPONSE.md",
        "README_ENHANCEMENT_SUMMARY.md",
        "FINAL_VERIFICATION_REPORT.md",
        "VIDEO_DEMO_SCRIPT.md",
        
        # Test images (small ones)
        "Test_img.jpg",
        "Test_img1.jpg",
        "test_image_smoke.jpg",
        
        # Git configuration
        ".gitignore",
        
        # MLflow
        "mlruns/",
        "mlflow.db",
    ]
    
    # Create ZIP file
    print(f"📦 Creating {zip_name}...")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in include_items:
            item_path = project_root / item
            
            if item_path.exists():
                if item_path.is_file():
                    # Add single file
                    zipf.write(item_path, item)
                    print(f"✅ Added file: {item}")
                elif item_path.is_dir():
                    # Add directory recursively
                    for file_path in item_path.rglob('*'):
                        if file_path.is_file():
                            # Calculate relative path
                            arcname = str(file_path.relative_to(project_root))
                            zipf.write(file_path, arcname)
                    print(f"✅ Added directory: {item} (with files)")
                else:
                    print(f"⚠️  Not found: {item}")
            else:
                print(f"❌ Missing: {item}")
    
    # Get ZIP file size
    zip_size = os.path.getsize(zip_name) / (1024 * 1024)  # MB
    print(f"\n📊 ZIP file created: {zip_name}")
    print(f"📏 Size: {zip_size:.2f} MB")
    
    # Verify ZIP contents
    print("\n🔍 Verifying ZIP contents...")
    with zipfile.ZipFile(zip_name, 'r') as zipf:
        file_list = zipf.namelist()
        print(f"📁 Total files in ZIP: {len(file_list)}")
        
        # Check critical files
        critical_files = [
            "Dockerfile",
            "requirements.txt", 
            "dvc.yaml",
            "smoke_tests.py",
            ".github/workflows/ci-cd.yml",
            "src/inference/app.py",
            "src/training/train.py",
            "models/best_model.pth"
        ]
        
        missing_in_zip = []
        for critical_file in critical_files:
            if not any(critical_file in path for path in file_list):
                missing_in_zip.append(critical_file)
        
        if missing_in_zip:
            print(f"❌ Missing in ZIP: {missing_in_zip}")
        else:
            print("✅ All critical files present in ZIP")
    
    print(f"\n🎯 Ready for submission: {zip_name}")
    return zip_name

def main():
    """Main function"""
    print("🚀 MLOps Assignment ZIP Preparation")
    print("=" * 50)
    
    # Clean up any existing ZIP
    existing_zip = "MLOps_Assignment_Complete.zip"
    if os.path.exists(existing_zip):
        os.remove(existing_zip)
        print(f"🗑️  Removed existing {existing_zip}")
    
    # Create new ZIP
    zip_file = create_assignment_zip()
    
    print("\n" + "=" * 50)
    print("✅ ZIP preparation complete!")
    print("📋 Deliverables included:")
    print("   • Complete source code")
    print("   • All configuration files")
    print("   • Model artifacts")
    print("   • CI/CD pipeline")
    print("   • Kubernetes manifests")
    print("   • Monitoring setup")
    print("   • Testing framework")
    print("   • Documentation")
    print("   • DVC configuration")
    print("   • Post-deployment evaluation")
    print("=" * 50)

if __name__ == "__main__":
    main()
