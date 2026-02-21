#!/usr/bin/env python3
"""
Post-deployment model evaluation script
Collects predictions and compares with true labels for performance tracking
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from datetime import datetime

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

import requests
from PIL import Image
import torch
from src.data.preprocessing import DataPreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostDeploymentEvaluator:
    """Post-deployment model performance evaluator"""
    
    def __init__(self, api_url: str = "http://localhost:8000", test_dir: str = "data/processed/test"):
        self.api_url = api_url
        self.test_dir = Path(test_dir)
        self.results = []
        
    def load_test_data(self) -> Tuple[List[str], List[str]]:
        """Load test images and their true labels"""
        image_paths = []
        true_labels = []
        
        for class_name in ['cat', 'dog']:
            class_dir = self.test_dir / class_name
            if class_dir.exists():
                for img_file in class_dir.glob('*.jpg'):
                    image_paths.append(str(img_file))
                    true_labels.append(class_name)
        
        return image_paths, true_labels
    
    def predict_batch(self, image_paths: List[str]) -> List[Dict]:
        """Get predictions for a batch of images"""
        predictions = []
        
        for img_path in image_paths:
            try:
                with open(img_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(f"{self.api_url}/predict", files=files, timeout=30)
                
                if response.status_code == 200:
                    pred_data = response.json()
                    predictions.append({
                        'image_path': img_path,
                        'predicted_class': pred_data['predicted_class'],
                        'confidence': pred_data['confidence'],
                        'probabilities': pred_data['probabilities']
                    })
                else:
                    logger.error(f"Failed to predict {img_path}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error predicting {img_path}: {str(e)}")
                
        return predictions
    
    def evaluate_performance(self, predictions: List[Dict], true_labels: List[str]) -> Dict:
        """Calculate performance metrics"""
        if len(predictions) != len(true_labels):
            raise ValueError("Predictions and true labels length mismatch")
        
        correct = 0
        total = len(predictions)
        confidences = []
        
        for pred, true_label in zip(predictions, true_labels):
            predicted_class = pred['predicted_class']
            confidence = pred['confidence']
            confidences.append(confidence)
            
            if predicted_class == true_label:
                correct += 1
        
        accuracy = correct / total if total > 0 else 0
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Calculate per-class metrics
        cat_correct = sum(1 for pred, true in zip(predictions, true_labels) 
                        if pred['predicted_class'] == 'cat' and true == 'cat')
        dog_correct = sum(1 for pred, true in zip(predictions, true_labels) 
                        if pred['predicted_class'] == 'dog' and true == 'dog')
        
        cat_total = sum(1 for true in true_labels if true == 'cat')
        dog_total = sum(1 for true in true_labels if true == 'dog')
        
        cat_accuracy = cat_correct / cat_total if cat_total > 0 else 0
        dog_accuracy = dog_correct / dog_total if dog_total > 0 else 0
        
        return {
            'overall_accuracy': accuracy,
            'average_confidence': avg_confidence,
            'total_predictions': total,
            'correct_predictions': correct,
            'cat_accuracy': cat_accuracy,
            'dog_accuracy': dog_accuracy,
            'cat_correct': cat_correct,
            'dog_correct': dog_correct,
            'cat_total': cat_total,
            'dog_total': dog_total,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, results: Dict, output_file: str = "post_deployment_evaluation.json"):
        """Save evaluation results to file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file}")
    
    def run_evaluation(self, save_to_file: bool = True):
        """Run complete post-deployment evaluation"""
        logger.info("Starting post-deployment evaluation...")
        
        # Load test data
        image_paths, true_labels = self.load_test_data()
        logger.info(f"Loaded {len(image_paths)} test images")
        
        if not image_paths:
            logger.error("No test images found!")
            return
        
        # Get predictions
        logger.info("Getting predictions from API...")
        predictions = self.predict_batch(image_paths)
        logger.info(f"Got {len(predictions)} predictions")
        
        # Evaluate performance
        logger.info("Evaluating performance...")
        results = self.evaluate_performance(predictions, true_labels)
        
        # Log results
        logger.info("Post-deployment evaluation results:")
        logger.info(f"Overall Accuracy: {results['overall_accuracy']:.2%}")
        logger.info(f"Average Confidence: {results['average_confidence']:.3f}")
        logger.info(f"Cat Accuracy: {results['cat_accuracy']:.2%} ({results['cat_correct']}/{results['cat_total']})")
        logger.info(f"Dog Accuracy: {results['dog_accuracy']:.2%} ({results['dog_correct']}/{results['dog_total']})")
        
        # Save results
        if save_to_file:
            self.save_results(results)
        
        return results

def main():
    """Main evaluation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Post-deployment model evaluation")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                       help="API endpoint URL")
    parser.add_argument("--test-dir", default="data/processed/test", 
                       help="Test images directory")
    parser.add_argument("--output", default="post_deployment_evaluation.json", 
                       help="Output file for results")
    parser.add_argument("--no-save", action="store_true", 
                       help="Don't save results to file")
    
    args = parser.parse_args()
    
    # Run evaluation
    evaluator = PostDeploymentEvaluator(args.api_url, args.test_dir)
    results = evaluator.run_evaluation(save_to_file=not args.no_save)
    
    # Print summary
    print("\n" + "="*60)
    print("POST-DEPLOYMENT EVALUATION SUMMARY")
    print("="*60)
    print(f"Overall Accuracy: {results['overall_accuracy']:.2%}")
    print(f"Average Confidence: {results['average_confidence']:.3f}")
    print(f"Total Predictions: {results['total_predictions']}")
    print(f"Correct Predictions: {results['correct_predictions']}")
    print(f"Cat Accuracy: {results['cat_accuracy']:.2%} ({results['cat_correct']}/{results['cat_total']})")
    print(f"Dog Accuracy: {results['dog_accuracy']:.2%} ({results['dog_correct']}/{results['dog_total']})")
    print(f"Evaluation Time: {results['timestamp']}")
    print("="*60)

if __name__ == "__main__":
    main()
