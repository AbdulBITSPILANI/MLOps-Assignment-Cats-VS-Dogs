#!/usr/bin/env python3
"""
Model Performance Monitoring for MLOps Pipeline
Tracks model accuracy and performance metrics post-deployment
"""
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelPerformanceMonitor:
    """Monitor model performance in production"""
    
    def __init__(self, api_url="http://localhost:8000", log_file="model_performance.json"):
        self.api_url = api_url
        self.log_file = Path(log_file)
        self.predictions_log = []
        self._load_existing_logs()
    
    def _load_existing_logs(self):
        """Load existing prediction logs"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.predictions_log = data.get('predictions', [])
                logger.info(f"Loaded {len(self.predictions_log)} existing predictions")
            except Exception as e:
                logger.error(f"Error loading logs: {e}")
                self.predictions_log = []
    
    def _save_logs(self):
        """Save prediction logs to file"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'total_predictions': len(self.predictions_log),
                'predictions': self.predictions_log
            }
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving logs: {e}")
    
    def log_prediction(self, image_path: str, predicted_class: str, 
                    actual_class: str = None, confidence: float = None):
        """Log a prediction with actual label if available"""
        prediction_entry = {
            'timestamp': datetime.now().isoformat(),
            'image_path': image_path,
            'predicted_class': predicted_class,
            'actual_class': actual_class,
            'confidence': confidence,
            'correct': actual_class == predicted_class if actual_class else None
        }
        
        self.predictions_log.append(prediction_entry)
        self._save_logs()
        
        logger.info(f"Logged prediction: {predicted_class} (confidence: {confidence:.2f})")
    
    def test_with_known_images(self, test_images_dir: str = "data/processed/test"):
        """Test model with known test images"""
        if not Path(test_images_dir).exists():
            logger.warning(f"Test directory not found: {test_images_dir}")
            return
        
        test_images = []
        for class_name in ['cat', 'dog']:
            class_dir = Path(test_images_dir) / class_name
            if class_dir.exists():
                images = list(class_dir.glob("*.jpg"))[:5]  # Test 5 images per class
                for img_path in images:
                    test_images.append((str(img_path), class_name))
        
        logger.info(f"Testing with {len(test_images)} known images")
        
        correct_predictions = 0
        total_predictions = 0
        
        for image_path, actual_class in test_images:
            try:
                # Make prediction
                with open(image_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(f"{self.api_url}/predict", files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    predicted_class = result.get('predicted_class')
                    confidence = result.get('confidence', 0)
                    
                    # Log prediction
                    self.log_prediction(image_path, predicted_class, actual_class, confidence)
                    
                    total_predictions += 1
                    if predicted_class == actual_class:
                        correct_predictions += 1
                    
                    time.sleep(0.5)  # Small delay between requests
                else:
                    logger.error(f"Prediction failed for {image_path}: {response.status_code}")
            
            except Exception as e:
                logger.error(f"Error testing {image_path}: {e}")
        
        # Calculate accuracy
        if total_predictions > 0:
            accuracy = (correct_predictions / total_predictions) * 100
            logger.info(f"Test accuracy: {accuracy:.2f}% ({correct_predictions}/{total_predictions})")
            return accuracy
        
        return 0.0
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics from logs"""
        if not self.predictions_log:
            return {}
        
        # Filter predictions with actual labels
        labeled_predictions = [p for p in self.predictions_log if p.get('actual_class')]
        
        if not labeled_predictions:
            return {}
        
        df = pd.DataFrame(labeled_predictions)
        
        # Calculate metrics
        correct = df['correct'].sum()
        total = len(df)
        accuracy = (correct / total) * 100
        
        # Confidence analysis
        avg_confidence = df['confidence'].mean()
        min_confidence = df['confidence'].min()
        max_confidence = df['confidence'].max()
        
        # Class-wise accuracy
        class_accuracy = {}
        for class_name in df['actual_class'].unique():
            class_df = df[df['actual_class'] == class_name]
            class_correct = class_df['correct'].sum()
            class_total = len(class_df)
            class_accuracy[class_name] = (class_correct / class_total) * 100
        
        # Recent performance (last 24 hours)
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=24)
        recent_predictions = [p for p in labeled_predictions 
                          if datetime.fromisoformat(p['timestamp']) > recent_cutoff]
        
        recent_accuracy = 0
        if recent_predictions:
            recent_correct = sum(1 for p in recent_predictions if p['correct'])
            recent_accuracy = (recent_correct / len(recent_predictions)) * 100
        
        return {
            'overall_accuracy': accuracy,
            'total_predictions': total,
            'recent_accuracy_24h': recent_accuracy,
            'recent_predictions_24h': len(recent_predictions),
            'average_confidence': avg_confidence,
            'confidence_range': {
                'min': min_confidence,
                'max': max_confidence
            },
            'class_accuracy': class_accuracy,
            'last_updated': datetime.now().isoformat()
        }
    
    def generate_performance_report(self) -> str:
        """Generate a performance report"""
        metrics = self.get_performance_metrics()
        
        if not metrics:
            return "No performance data available. Run tests with known images first."
        
        report = f"""
Model Performance Report
{'='*50}

Overall Performance:
   • Accuracy: {metrics['overall_accuracy']:.2f}%
   • Total Predictions: {metrics['total_predictions']}
   • Average Confidence: {metrics['average_confidence']:.2f}

Recent Performance (24h):
   • Recent Accuracy: {metrics['recent_accuracy_24h']:.2f}%
   • Recent Predictions: {metrics['recent_predictions_24h']}

Class-wise Performance:
"""
        
        for class_name, accuracy in metrics.get('class_accuracy', {}).items():
            report += f"   • {class_name.capitalize()}: {accuracy:.2f}%\n"
        
        report += f"""
Confidence Range:
   • Min: {metrics['confidence_range']['min']:.2f}
   • Max: {metrics['confidence_range']['max']:.2f}

Last Updated: {metrics['last_updated']}

{'='*50}
"""
        return report
    
    def check_model_drift(self, threshold: float = 5.0) -> bool:
        """Check for model performance drift"""
        metrics = self.get_performance_metrics()
        
        if not metrics:
            return False
        
        overall_acc = metrics['overall_accuracy']
        recent_acc = metrics['recent_accuracy_24h']
        
        if recent_acc == 0:  # No recent data
            return False
        
        drift = overall_acc - recent_acc
        
        if drift > threshold:
            logger.warning(f"Model drift detected! Overall: {overall_acc:.2f}%, Recent: {recent_acc:.2f}% (drift: {drift:.2f}%)")
            return True
        
        return False

def main():
    """Main monitoring execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor model performance")
    parser.add_argument("--test-dir", default="data/processed/test", help="Test images directory")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    parser.add_argument("--report", action="store_true", help="Generate performance report")
    parser.add_argument("--check-drift", action="store_true", help="Check for model drift")
    
    args = parser.parse_args()
    
    monitor = ModelPerformanceMonitor(args.api_url)
    
    if args.report:
        print(monitor.generate_performance_report())
    
    if args.check_drift:
        if monitor.check_model_drift():
            print("Model drift detected! Consider retraining.")
        else:
            print("No significant model drift detected.")
    
    if args.test_dir:
        accuracy = monitor.test_with_known_images(args.test_dir)
        print(f"\nTest completed. Accuracy: {accuracy:.2f}%")
    
    return 0

if __name__ == "__main__":
    exit(main())
