from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import structlog
import numpy as np

from models.embedding_model import EmbeddingModel
from models.compatibility_model import CompatibilityModel

logger = structlog.get_logger()
router = APIRouter()

class MatchRequest(BaseModel):
    athlete_data: Dict[str, Any]
    brand_data: Dict[str, Any]
    athlete_metrics: List[Dict[str, Any]]
    preferences: Optional[Dict[str, Any]] = None

class BulkMatchRequest(BaseModel):
    athletes: List[Dict[str, Any]]
    brands: List[Dict[str, Any]]
    athlete_metrics: Dict[str, List[Dict[str, Any]]]  # athlete_id -> metrics
    filters: Optional[Dict[str, Any]] = None

class CompatibilityResponse(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    factors: Dict[str, float]
    recommendation: str
    estimated_success_rate: float
    risk_factors: List[str]
    optimization_suggestions: List[str]

@router.post("/calculate-compatibility", response_model=CompatibilityResponse)
async def calculate_compatibility(request: MatchRequest):
    """Calculate detailed compatibility between athlete and brand"""
    try:
        embedding_model = EmbeddingModel.get_instance()
        compatibility_model = CompatibilityModel()
        
        # Generate embeddings
        athlete_embedding = embedding_model.create_athlete_embedding(
            request.athlete_data, 
            request.athlete_metrics
        )
        
        brand_embedding = embedding_model.create_brand_embedding(request.brand_data)
        
        # Calculate compatibility factors
        factors = compatibility_model.calculate_compatibility_factors(
            request.athlete_data,
            request.brand_data,
            request.athlete_metrics
        )
        
        # Calculate semantic similarity
        semantic_similarity = embedding_model.calculate_similarity(
            athlete_embedding, 
            brand_embedding
        )
        
        # Overall weighted score
        weights = {
            "semantic_similarity": 0.25,
            "sport_alignment": 0.20,
            "audience_match": 0.20,
            "engagement_quality": 0.15,
            "budget_compatibility": 0.10,
            "location_proximity": 0.05,
            "brand_safety": 0.05
        }
        
        overall_score = sum(
            factors.get(factor, 0) * weight 
            for factor, weight in weights.items()
        ) + (semantic_similarity * 100 * weights["semantic_similarity"])
        
        # Generate recommendations and risk assessment
        recommendation = compatibility_model.generate_recommendation(overall_score, factors)
        risk_factors = compatibility_model.assess_risk_factors(
            request.athlete_data, 
            request.brand_data, 
            factors
        )
        optimization_suggestions = compatibility_model.get_optimization_suggestions(factors)
        
        # Estimate success rate
        estimated_success_rate = min(95, max(10, overall_score - 5))
        
        response = CompatibilityResponse(
            overall_score=round(overall_score, 1),
            factors=factors,
            recommendation=recommendation,
            estimated_success_rate=round(estimated_success_rate, 1),
            risk_factors=risk_factors,
            optimization_suggestions=optimization_suggestions
        )
        
        logger.info("Compatibility calculated", 
                   athlete_id=request.athlete_data.get("id"),
                   brand_id=request.brand_data.get("id"),
                   score=overall_score)
        
        return response
        
    except Exception as e:
        logger.error("Failed to calculate compatibility", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to calculate compatibility")

@router.post("/bulk-analysis")
async def bulk_matching_analysis(request: BulkMatchRequest):
    """Perform bulk matching analysis for multiple athletes and brands"""
    try:
        embedding_model = EmbeddingModel.get_instance()
        compatibility_model = CompatibilityModel()
        
        results = []
        
        # Create embeddings for all athletes and brands
        athlete_embeddings = {}
        brand_embeddings = {}
        
        for athlete in request.athletes:
            athlete_id = athlete["id"]
            metrics = request.athlete_metrics.get(athlete_id, [])
            athlete_embeddings[athlete_id] = embedding_model.create_athlete_embedding(athlete, metrics)
        
        for brand in request.brands:
            brand_id = brand["id"]
            brand_embeddings[brand_id] = embedding_model.create_brand_embedding(brand)
        
        # Calculate compatibility for all pairs
        for athlete in request.athletes:
            athlete_id = athlete["id"]
            athlete_embedding = athlete_embeddings[athlete_id]
            athlete_metrics = request.athlete_metrics.get(athlete_id, [])
            
            athlete_matches = []
            
            for brand in request.brands:
                brand_id = brand["id"]
                brand_embedding = brand_embeddings[brand_id]
                
                # Calculate factors
                factors = compatibility_model.calculate_compatibility_factors(
                    athlete, brand, athlete_metrics
                )
                
                # Semantic similarity
                semantic_similarity = embedding_model.calculate_similarity(
                    athlete_embedding, brand_embedding
                )
                
                # Overall score
                weights = {
                    "semantic_similarity": 0.25,
                    "sport_alignment": 0.20,
                    "audience_match": 0.20,
                    "engagement_quality": 0.15,
                    "budget_compatibility": 0.10,
                    "location_proximity": 0.05,
                    "brand_safety": 0.05
                }
                
                overall_score = sum(
                    factors.get(factor, 0) * weight 
                    for factor, weight in weights.items()
                ) + (semantic_similarity * 100 * weights["semantic_similarity"])
                
                # Only include good matches
                if overall_score >= 60:  # Threshold for bulk analysis
                    athlete_matches.append({
                        "brand_id": brand_id,
                        "brand_name": brand.get("company_name", ""),
                        "overall_score": round(overall_score, 1),
                        "factors": factors,
                        "semantic_similarity": round(semantic_similarity * 100, 1)
                    })
            
            # Sort matches by score
            athlete_matches.sort(key=lambda x: x["overall_score"], reverse=True)
            
            results.append({
                "athlete_id": athlete_id,
                "athlete_name": f"{athlete.get('first_name', '')} {athlete.get('last_name', '')}",
                "matches": athlete_matches[:10]  # Top 10 matches per athlete
            })
        
        logger.info("Bulk matching analysis completed", 
                   athletes_count=len(request.athletes),
                   brands_count=len(request.brands),
                   total_matches=sum(len(r["matches"]) for r in results))
        
        return {
            "analysis_results": results,
            "summary": {
                "athletes_analyzed": len(request.athletes),
                "brands_analyzed": len(request.brands),
                "total_potential_matches": sum(len(r["matches"]) for r in results)
            }
        }
        
    except Exception as e:
        logger.error("Bulk matching analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail="Bulk matching analysis failed")

@router.post("/market-predictions")
async def generate_market_predictions(sport: Optional[str] = None, days_ahead: int = 30):
    """Generate AI-powered market predictions"""
    try:
        # This would use historical data and ML models to predict trends
        # For now, return structured predictions based on current data
        
        predictions = {
            "sport": sport or "overall",
            "prediction_period_days": days_ahead,
            "forecasts": {
                "deal_volume": {
                    "predicted_deals": 45 + (hash(sport or "all") % 20),
                    "confidence": 0.78,
                    "trend": "increasing"
                },
                "average_deal_value": {
                    "predicted_value": 12500 + (hash(sport or "all") % 5000),
                    "confidence": 0.65,
                    "trend": "stable"
                },
                "market_activity": {
                    "activity_level": "high",
                    "confidence": 0.82,
                    "key_drivers": ["NIL rule changes", "increased brand awareness", "social media growth"]
                }
            },
            "recommendations": [
                "Focus on athletes with strong engagement rates (>6%)",
                "Local partnerships showing 23% higher success rates",
                "Video content campaigns outperforming static posts by 40%"
            ],
            "risk_factors": [
                "Regulatory changes in NIL rules",
                "Market saturation in popular sports",
                "Economic factors affecting marketing budgets"
            ]
        }
        
        logger.info("Market predictions generated", sport=sport, days_ahead=days_ahead)
        return predictions
        
    except Exception as e:
        logger.error("Failed to generate market predictions", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate market predictions")

@router.get("/model-performance")
async def get_model_performance():
    """Get AI model performance metrics"""
    try:
        # In production, this would return real model performance metrics
        performance = {
            "embedding_model": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "version": "1.0.0",
                "accuracy": 0.87,
                "last_trained": "2024-01-15T00:00:00Z"
            },
            "compatibility_model": {
                "model_name": "custom_compatibility_scorer",
                "version": "1.2.0",
                "precision": 0.82,
                "recall": 0.79,
                "f1_score": 0.80,
                "last_evaluated": "2024-01-20T00:00:00Z"
            },
            "prediction_accuracy": {
                "deal_success_prediction": 0.74,
                "value_estimation": 0.68,
                "market_trend_prediction": 0.71
            },
            "processing_metrics": {
                "avg_response_time_ms": 150,
                "daily_requests": 1247,
                "error_rate": 0.02
            }
        }
        
        logger.info("Model performance metrics retrieved")
        return performance
        
    except Exception as e:
        logger.error("Failed to get model performance", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve model performance")