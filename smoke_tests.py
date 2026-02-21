#!/usr/bin/env python3
"""
Smoke tests for MLOps pipeline deployment
"""
import requests
import time
import json
import sys
from pathlib import Path

class SmokeTest:
    """Smoke test suite for MLOps deployment"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy" and data.get("model_loaded"):
                    self.test_results.append(("Health Check", "PASS", "Service is healthy"))
                    return True
                else:
                    self.test_results.append(("Health Check", "FAIL", f"Invalid response: {data}"))
                    return False
            else:
                self.test_results.append(("Health Check", "FAIL", f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            self.test_results.append(("Health Check", "FAIL", str(e)))
            return False
    
    def test_prediction_endpoint(self):
        """Test prediction endpoint with sample image"""
        try:
            # Create a simple test image if not exists
            test_image_path = "test_image_smoke.jpg"
            if not Path(test_image_path).exists():
                self._create_test_image(test_image_path)
            
            with open(test_image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.base_url}/predict", files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "predicted_class" in data and "confidence" in data:
                    confidence = data["confidence"]
                    if confidence > 0:
                        self.test_results.append(("Prediction", "PASS", f"Prediction works (confidence: {confidence:.2f})"))
                        return True
                    else:
                        self.test_results.append(("Prediction", "FAIL", f"Zero confidence: {confidence}"))
                        return False
                else:
                    self.test_results.append(("Prediction", "FAIL", f"Invalid response format: {data}"))
                    return False
            else:
                self.test_results.append(("Prediction", "FAIL", f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            self.test_results.append(("Prediction", "FAIL", str(e)))
            return False
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            if response.status_code == 200 and "inference_requests_total" in response.text:
                self.test_results.append(("Metrics", "PASS", "Metrics endpoint working"))
                return True
            else:
                self.test_results.append(("Metrics", "FAIL", "Metrics not available"))
                return False
        except Exception as e:
            self.test_results.append(("Metrics", "FAIL", str(e)))
            return False
    
    def test_monitoring_services(self):
        """Test monitoring services"""
        monitoring_services = [
            ("Grafana", "http://localhost:3000"),
            ("Prometheus", "http://localhost:9090"),
            ("MLflow", "http://localhost:5000")
        ]
        
        all_pass = True
        for service_name, url in monitoring_services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.test_results.append((service_name, "PASS", "Service accessible"))
                else:
                    self.test_results.append((service_name, "FAIL", f"HTTP {response.status_code}"))
                    all_pass = False
            except Exception as e:
                # MLflow is optional, so don't fail the test if it's not running
                if service_name == "MLflow":
                    self.test_results.append((service_name, "SKIP", f"Service not running (optional): {str(e)[:50]}"))
                else:
                    self.test_results.append((service_name, "FAIL", str(e)))
                    all_pass = False
        
        return all_pass
    
    def _create_test_image(self, path):
        """Create a simple test image"""
        try:
            from PIL import Image
            import numpy as np
            
            # Create a simple 224x224 RGB image
            img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(path)
        except ImportError:
            # If PIL not available, create a minimal file
            with open(path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x00IDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01')
    
    def run_all_tests(self):
        """Run all smoke tests"""
        print("Running MLOps Pipeline Smoke Tests")
        print("=" * 50)
        
        # Wait for services to start
        print("Waiting for services to start...")
        time.sleep(10)
        
        # Run tests
        self.test_health_endpoint()
        self.test_prediction_endpoint()
        self.test_metrics_endpoint()
        self.test_monitoring_services()
        
        # Print results
        print("\nTest Results:")
        print("-" * 50)
        
        passed = 0
        total = len(self.test_results)
        failed = 0
        skipped = 0
        
        for test_name, status, message in self.test_results:
            status_symbol = "PASS" if status == "PASS" else "SKIP" if status == "SKIP" else "FAIL"
            print(f"{status_symbol} {test_name}: {status} - {message}")
            if status == "PASS":
                passed += 1
            elif status == "FAIL":
                failed += 1
            else:
                skipped += 1
        
        print("-" * 50)
        print(f"Overall: {passed}/{total} tests passed ({skipped} skipped)")
        
        # Consider tests successful if no failures (skips are ok)
        if failed == 0:
            print("All critical tests passed! Deployment successful!")
            return True
        else:
            print(f"{failed} tests failed. Check deployment.")
            return False

def main():
    """Main smoke test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run smoke tests for MLOps deployment")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for API")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit with error code on failure")
    
    args = parser.parse_args()
    
    smoke_test = SmokeTest(args.url)
    success = smoke_test.run_all_tests()
    
    if not success and args.fail_on_error:
        sys.exit(1)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
