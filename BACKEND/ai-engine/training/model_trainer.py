import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error
import joblib
import structlog
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

logger = structlog.get_logger()

class ModelTrainer:
    """Handles training and evaluation of ML models"""
    
    def __init__(self):
        self.model_dir = os.getenv("MODEL_CHECKPOINT_DIR", "./checkpoints")
        self.training_status = {}  # In production, this would be in Redis
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
    
    async def train_model(self, training_id: str, model_type: str, data_days: int = 90,
                         validation_split: float = 0.2, hyperparameters: Dict = None):
        """Train a specific model type"""
        try:
            self.training_status[training_id] = {
                "status": "preparing_data",
                "progress": 0,
                "started_at": datetime.now().isoformat()
            }
            
            # Prepare training data
            logger.info("Preparing training data", training_id=training_id, model_type=model_type)
            data_processor = DataProcessor()
            training_data = await data_processor.prepare_training_data(model_type, data_days)
            
            if not training_data or len(training_data) < 50:
                raise Exception(f"Insufficient training data: {len(training_data) if training_data else 0} samples")
            
            self.training_status[training_id]["status"] = "training"
            self.training_status[training_id]["progress"] = 25
            
            # Train model based on type
            if model_type == "compatibility":
                model, metrics = await self._train_compatibility_model(training_data, validation_split)
            elif model_type == "success_prediction":
                model, metrics = await self._train_success_prediction_model(training_data, validation_split)
            elif model_type == "value_estimation":
                model, metrics = await self._train_value_estimation_model(training_data, validation_split)
            else:
                raise Exception(f"Unknown model type: {model_type}")
            
            self.training_status[training_id]["status"] = "saving"
            self.training_status[training_id]["progress"] = 90
            
            # Save trained model
            model_path = os.path.join(self.model_dir, f"{model_type}_model.joblib")
            joblib.dump(model, model_path)
            
            # Save metrics
            metrics_path = os.path.join(self.model_dir, f"{model_type}_metrics.json")
            import json
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            self.training_status[training_id] = {
                "status": "completed",
                "progress": 100,
                "started_at": self.training_status[training_id]["started_at"],
                "completed_at": datetime.now().isoformat(),
                "metrics": metrics,
                "model_path": model_path
            }
            
            logger.info("Model training completed", 
                       training_id=training_id,
                       model_type=model_type,
                       accuracy=metrics.get("accuracy", 0))
            
        except Exception as e:
            self.training_status[training_id] = {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
            logger.error("Model training failed", training_id=training_id, error=str(e))
            raise
    
    async def _train_compatibility_model(self, data: List[Dict], validation_split: float):
        """Train compatibility scoring model"""
        # Prepare features and labels
        features = []
        labels = []
        
        for sample in data:
            feature_vector = [
                sample.get("sport_alignment", 0),
                sample.get("audience_match", 0),
                sample.get("engagement_quality", 0),
                sample.get("budget_fit", 0),
                sample.get("location_proximity", 0),
                sample.get("athlete_followers", 0) / 1000,  # Normalize
                sample.get("brand_budget", 0) / 1000,      # Normalize
            ]
            features.append(feature_vector)
            
            # Binary label: high compatibility (>70) vs low compatibility
            labels.append(1 if sample.get("compatibility_score", 0) > 70 else 0)
        
        X = np.array(features)
        y = np.array(labels)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        # Train Random Forest
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_val)
        metrics = {
            "accuracy": accuracy_score(y_val, y_pred),
            "precision": precision_score(y_val, y_pred),
            "recall": recall_score(y_val, y_pred),
            "f1_score": f1_score(y_val, y_pred),
            "training_samples": len(X_train),
            "validation_samples": len(X_val)
        }
        
        return model, metrics
    
    async def _train_success_prediction_model(self, data: List[Dict], validation_split: float):
        """Train campaign success prediction model"""
        # Mock implementation - would use real historical campaign data
        features = np.random.rand(len(data), 8)  # Mock features
        labels = np.random.randint(0, 2, len(data))  # Mock binary success labels
        
        X_train, X_val, y_train, y_val = train_test_split(
            features, labels, test_size=validation_split, random_state=42
        )
        
        model = RandomForestClassifier(n_estimators=80, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_val)
        metrics = {
            "accuracy": accuracy_score(y_val, y_pred),
            "precision": precision_score(y_val, y_pred),
            "recall": recall_score(y_val, y_pred),
            "f1_score": f1_score(y_val, y_pred),
            "training_samples": len(X_train),
            "validation_samples": len(X_val)
        }
        
        return model, metrics
    
    async def _train_value_estimation_model(self, data: List[Dict], validation_split: float):
        """Train deal value estimation model"""
        # Mock implementation - would use real deal value data
        features = np.random.rand(len(data), 6)  # Mock features
        labels = np.random.rand(len(data)) * 50000  # Mock deal values
        
        X_train, X_val, y_train, y_val = train_test_split(
            features, labels, test_size=validation_split, random_state=42
        )
        
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_val)
        metrics = {
            "mean_absolute_error": mean_absolute_error(y_val, y_pred),
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "r2_score": model.score(X_val, y_val)
        }
        
        return model, metrics
    
    def get_training_status(self, training_id: str) -> Optional[Dict]:
        """Get status of ongoing training job"""
        return self.training_status.get(training_id)
    
    def estimate_training_time(self, model_type: str) -> int:
        """Estimate training time in minutes"""
        estimates = {
            "compatibility": 15,
            "success_prediction": 20,
            "value_estimation": 12
        }
        return estimates.get(model_type, 15)
    
    def evaluate_model(self, model_type: str, test_data: List[Dict]) -> Dict:
        """Evaluate existing model on test data"""
        try:
            model_path = os.path.join(self.model_dir, f"{model_type}_model.joblib")
            
            if not os.path.exists(model_path):
                raise Exception(f"Model not found: {model_path}")
            
            model = joblib.load(model_path)
            
            # Prepare test features (simplified)
            test_features = np.random.rand(len(test_data), 8)  # Mock for demo
            test_labels = np.random.randint(0, 2, len(test_data))
            
            predictions = model.predict(test_features)
            
            if model_type in ["compatibility", "success_prediction"]:
                # Classification metrics
                metrics = {
                    "accuracy": accuracy_score(test_labels, predictions),
                    "precision": precision_score(test_labels, predictions, zero_division=0),
                    "recall": recall_score(test_labels, predictions, zero_division=0),
                    "f1_score": f1_score(test_labels, predictions, zero_division=0)
                }
            else:
                # Regression metrics
                test_values = np.random.rand(len(test_data)) * 50000
                metrics = {
                    "mean_absolute_error": mean_absolute_error(test_values, predictions),
                    "r2_score": 0.72  # Mock score
                }
            
            return metrics
            
        except Exception as e:
            logger.error("Model evaluation failed", model_type=model_type, error=str(e))
            raise
    
    def grade_model_performance(self, metrics: Dict) -> str:
        """Grade model performance as A, B, C, D, or F"""
        if "accuracy" in metrics:
            score = metrics["accuracy"]
        elif "r2_score" in metrics:
            score = metrics["r2_score"]
        else:
            return "F"
        
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"  
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def get_improvement_recommendations(self, model_type: str, metrics: Dict) -> List[str]:
        """Get recommendations for improving model performance"""
        recommendations = []
        
        if "accuracy" in metrics and metrics["accuracy"] < 0.8:
            recommendations.append("Consider collecting more training data")
            recommendations.append("Feature engineering may improve performance")
        
        if "precision" in metrics and metrics["precision"] < 0.75:
            recommendations.append("Reduce false positives by adjusting classification threshold")
        
        if "recall" in metrics and metrics["recall"] < 0.75:
            recommendations.append("Improve feature quality to capture more positive cases")
        
        if model_type == "value_estimation":
            if metrics.get("mean_absolute_error", 0) > 5000:
                recommendations.append("Value estimation error is high - review feature selection")
        
        if not recommendations:
            recommendations.append("Model performance is satisfactory")
        
        return recommendations


class DataProcessor:
    """Processes data for model training"""
    
    async def prepare_training_data(self, model_type: str, days: int) -> List[Dict]:
        """Prepare training data for specified model type"""
        # Mock training data - in production would fetch from PocketBase
        logger.info("Preparing training data", model_type=model_type, days=days)
        
        if model_type == "compatibility":
            return self._generate_compatibility_training_data()
        elif model_type == "success_prediction":
            return self._generate_success_prediction_data()
        elif model_type == "value_estimation":
            return self._generate_value_estimation_data()
        else:
            return []
    
    async def prepare_evaluation_data(self, model_type: str, days: int) -> List[Dict]:
        """Prepare evaluation data"""
        return await self.prepare_training_data(model_type, days)
    
    def _generate_compatibility_training_data(self) -> List[Dict]:
        """Generate mock compatibility training data"""
        data = []
        for i in range(200):
            sample = {
                "athlete_id": f"athlete_{i}",
                "brand_id": f"brand_{i % 50}",
                "sport_alignment": np.random.uniform(20, 100),
                "audience_match": np.random.uniform(30, 95),
                "engagement_quality": np.random.uniform(10, 100),
                "budget_fit": np.random.uniform(20, 100),
                "location_proximity": np.random.uniform(10, 100),
                "athlete_followers": np.random.randint(1000, 500000),
                "brand_budget": np.random.randint(2000, 100000),
                "compatibility_score": np.random.uniform(30, 95)
            }
            data.append(sample)
        return data
    
    def _generate_success_prediction_data(self) -> List[Dict]:
        """Generate mock success prediction training data"""
        data = []
        for i in range(150):
            sample = {
                "campaign_id": f"campaign_{i}",
                "budget": np.random.randint(5000, 100000),
                "duration_days": np.random.randint(7, 90),
                "athlete_followers": np.random.randint(5000, 1000000),
                "engagement_rate": np.random.uniform(2, 15),
                "brand_industry_match": np.random.uniform(0.4, 1.0),
                "success": np.random.choice([0, 1], p=[0.3, 0.7])  # 70% success rate
            }
            data.append(sample)
        return data
    
    def _generate_value_estimation_data(self) -> List[Dict]:
        """Generate mock value estimation training data"""
        data = []
        for i in range(180):
            followers = np.random.randint(5000, 500000)
            engagement = np.random.uniform(2, 12)
            
            # Mock value based on followers and engagement
            base_value = followers * 0.02
            engagement_multiplier = 1 + (engagement / 10)
            estimated_value = base_value * engagement_multiplier * np.random.uniform(0.8, 1.2)
            
            sample = {
                "deal_id": f"deal_{i}",
                "athlete_followers": followers,
                "engagement_rate": engagement,
                "sport_popularity": np.random.uniform(0.6, 1.0),
                "brand_budget": np.random.randint(10000, 200000),
                "location_factor": np.random.uniform(0.8, 1.2),
                "actual_value": max(1000, min(100000, estimated_value))
            }
            data.append(sample)
        return data