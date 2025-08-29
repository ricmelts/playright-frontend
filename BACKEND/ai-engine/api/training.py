from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import structlog
from datetime import datetime

from training.model_trainer import ModelTrainer
from training.data_processor import DataProcessor

logger = structlog.get_logger()
router = APIRouter()

class TrainingRequest(BaseModel):
    model_type: str  # "compatibility", "success_prediction", "value_estimation"
    training_data_days: int = 90
    validation_split: float = 0.2
    hyperparameters: Optional[Dict[str, Any]] = None

class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    validation_samples: int
    training_time_minutes: float

@router.post("/start-training")
async def start_model_training(
    request: TrainingRequest, 
    background_tasks: BackgroundTasks
):
    """Start training a new ML model in the background"""
    try:
        trainer = ModelTrainer()
        
        # Validate model type
        valid_models = ["compatibility", "success_prediction", "value_estimation"]
        if request.model_type not in valid_models:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model type. Must be one of: {valid_models}"
            )
        
        # Start training in background
        training_id = f"training_{request.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        background_tasks.add_task(
            trainer.train_model,
            training_id=training_id,
            model_type=request.model_type,
            data_days=request.training_data_days,
            validation_split=request.validation_split,
            hyperparameters=request.hyperparameters or {}
        )
        
        logger.info("Model training started", 
                   training_id=training_id,
                   model_type=request.model_type)
        
        return {
            "training_id": training_id,
            "status": "started",
            "model_type": request.model_type,
            "estimated_duration_minutes": trainer.estimate_training_time(request.model_type),
            "message": "Training started in background. Use /training/status to check progress."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start model training", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to start training")

@router.get("/status/{training_id}")
async def get_training_status(training_id: str):
    """Get status of ongoing model training"""
    try:
        trainer = ModelTrainer()
        status = trainer.get_training_status(training_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Training job not found")
        
        logger.info("Training status retrieved", training_id=training_id, status=status["status"])
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get training status", training_id=training_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get training status")

@router.post("/evaluate-model")
async def evaluate_model(model_type: str, test_data_days: int = 30):
    """Evaluate model performance on recent data"""
    try:
        trainer = ModelTrainer()
        
        # Get test data
        data_processor = DataProcessor()
        test_data = await data_processor.prepare_evaluation_data(
            model_type=model_type,
            days=test_data_days
        )
        
        if not test_data or len(test_data) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Insufficient test data for evaluation"
            )
        
        # Run evaluation
        metrics = trainer.evaluate_model(model_type, test_data)
        
        evaluation_result = {
            "model_type": model_type,
            "evaluation_date": datetime.now().isoformat(),
            "test_period_days": test_data_days,
            "metrics": metrics,
            "performance_grade": trainer.grade_model_performance(metrics),
            "recommendations": trainer.get_improvement_recommendations(model_type, metrics)
        }
        
        logger.info("Model evaluation completed", 
                   model_type=model_type,
                   test_samples=len(test_data),
                   accuracy=metrics.get("accuracy", 0))
        
        return evaluation_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Model evaluation failed", model_type=model_type, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to evaluate model")

@router.get("/model-info")
async def get_model_info():
    """Get information about all deployed models"""
    try:
        models_info = {
            "embedding_model": {
                "name": "sentence-transformers/all-MiniLM-L6-v2",
                "type": "sentence_transformer",
                "version": "2.2.2",
                "purpose": "Generate semantic embeddings for athletes and brands",
                "input_dimension": "variable_text",
                "output_dimension": 384,
                "last_updated": "2024-01-15T00:00:00Z",
                "status": "active"
            },
            "compatibility_model": {
                "name": "custom_compatibility_scorer",
                "type": "ensemble",
                "version": "1.2.0",
                "purpose": "Calculate multi-factor compatibility scores",
                "features": [
                    "sport_alignment", "audience_demographics", "engagement_quality",
                    "budget_fit", "location_proximity", "brand_safety"
                ],
                "last_trained": "2024-01-20T00:00:00Z",
                "status": "active"
            },
            "success_prediction_model": {
                "name": "campaign_success_predictor",
                "type": "random_forest",
                "version": "1.1.0",
                "purpose": "Predict campaign success probability",
                "accuracy": 0.74,
                "last_trained": "2024-01-18T00:00:00Z",
                "status": "active"
            },
            "value_estimation_model": {
                "name": "deal_value_estimator",
                "type": "gradient_boosting",
                "version": "1.0.5",
                "purpose": "Estimate fair deal values",
                "mean_absolute_error": 0.12,
                "last_trained": "2024-01-22T00:00:00Z", 
                "status": "active"
            }
        }
        
        # Add system performance metrics
        system_performance = {
            "total_predictions_today": 1247,
            "average_response_time_ms": 145,
            "error_rate_24h": 0.018,
            "model_accuracy_average": 0.76,
            "last_health_check": datetime.now().isoformat()
        }
        
        return {
            "models": models_info,
            "system_performance": system_performance,
            "api_version": "1.0.0"
        }
        
    except Exception as e:
        logger.error("Failed to get model info", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve model information")

@router.post("/retrain-models")
async def schedule_model_retraining(background_tasks: BackgroundTasks):
    """Schedule retraining of all models with latest data"""
    try:
        trainer = ModelTrainer()
        
        models_to_retrain = ["compatibility", "success_prediction", "value_estimation"]
        training_jobs = []
        
        for model_type in models_to_retrain:
            training_id = f"retrain_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            background_tasks.add_task(
                trainer.train_model,
                training_id=training_id,
                model_type=model_type,
                data_days=180,  # Use 6 months of data for retraining
                validation_split=0.15
            )
            
            training_jobs.append({
                "training_id": training_id,
                "model_type": model_type,
                "status": "queued"
            })
        
        logger.info("Model retraining scheduled", jobs_count=len(training_jobs))
        
        return {
            "message": "Model retraining scheduled",
            "training_jobs": training_jobs,
            "estimated_completion": "2-4 hours"
        }
        
    except Exception as e:
        logger.error("Failed to schedule model retraining", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to schedule model retraining")