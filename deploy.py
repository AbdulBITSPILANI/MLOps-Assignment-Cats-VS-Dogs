#!/usr/bin/env python3
"""
Automated Deployment Script for MLOps Pipeline
Supports both Docker Compose and Kubernetes deployment
"""
import subprocess
import time
import argparse
import sys
import requests
from pathlib import Path

class DeploymentManager:
    """Manage MLOps pipeline deployment"""
    
    def __init__(self, deployment_type="docker"):
        self.deployment_type = deployment_type
        self.base_url = "http://localhost:8000"
    
    def run_command(self, command: str, check: bool = True) -> bool:
        """Run shell command and return success status"""
        try:
            print(f"Running: {command}")
            result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Success: {command}")
                return True
            else:
                print(f"Failed: {command}")
                print(f"Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"Exception: {e}")
            return False
    
    def deploy_docker_compose(self):
        """Deploy using Docker Compose"""
        print("Deploying with Docker Compose...")
        
        commands = [
            "docker-compose down",
            "docker-compose build --no-cache",
            "docker-compose up -d"
        ]
        
        for cmd in commands:
            if not self.run_command(cmd):
                return False
        
        return True
    
    def deploy_kubernetes(self):
        """Deploy to Kubernetes cluster"""
        print("Deploying to Kubernetes...")
        
        commands = [
            "kubectl apply -f k8s/",
            "kubectl rollout status deployment/cats-dogs-inference",
            "kubectl get services"
        ]
        
        for cmd in commands:
            if not self.run_command(cmd):
                return False
        
        return True
    
    def wait_for_deployment(self, max_wait: int = 300) -> bool:
        """Wait for deployment to be ready"""
        print(f"Waiting for deployment (max {max_wait}s)...")
        
        for i in range(max_wait // 10):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("Deployment is ready!")
                    return True
            except:
                pass
            
            time.sleep(10)
            print(f"Waiting... ({i * 10}s)")
        
        print("Deployment timeout!")
        return False
    
    def run_smoke_tests(self) -> bool:
        """Run smoke tests after deployment"""
        print("Running smoke tests...")
        
        try:
            # Import and run smoke tests
            sys.path.append('.')
            from smoke_tests import SmokeTest
            
            smoke_test = SmokeTest(self.base_url)
            return smoke_test.run_all_tests()
            
        except Exception as e:
            print(f"Smoke tests failed: {e}")
            return False
    
    def deploy(self, run_tests: bool = True) -> bool:
        """Complete deployment process"""
        print(f"Starting {self.deployment_type} deployment...")
        
        # Deploy based on type
        if self.deployment_type == "docker":
            if not self.deploy_docker_compose():
                return False
        elif self.deployment_type == "k8s":
            if not self.deploy_kubernetes():
                return False
        else:
            print(f"Unknown deployment type: {self.deployment_type}")
            return False
        
        # Wait for deployment
        if not self.wait_for_deployment():
            return False
        
        # Run smoke tests
        if run_tests:
            if not self.run_smoke_tests():
                return False
        
        print("Deployment completed successfully!")
        return True
    
    def rollback(self):
        """Rollback deployment"""
        print("Rolling back deployment...")
        
        if self.deployment_type == "docker":
            self.run_command("docker-compose down")
        elif self.deployment_type == "k8s":
            self.run_command("kubectl rollout undo deployment/cats-dogs-inference")
        
        print("Rollback completed")

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Deploy MLOps pipeline")
    parser.add_argument("--type", choices=["docker", "k8s"], 
                       default="docker", help="Deployment type")
    parser.add_argument("--no-tests", action="store_true", 
                       help="Skip smoke tests")
    parser.add_argument("--rollback", action="store_true", 
                       help="Rollback deployment")
    
    args = parser.parse_args()
    
    deployer = DeploymentManager(args.type)
    
    if args.rollback:
        deployer.rollback()
        return 0
    
    success = deployer.deploy(run_tests=not args.no_tests)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
