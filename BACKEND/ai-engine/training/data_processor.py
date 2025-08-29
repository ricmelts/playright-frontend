import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog
import json

logger = structlog.get_logger()

class DataProcessor:
    """Processes and prepares data for ML model training"""
    
    def __init__(self):
        self.feature_columns = {
            "compatibility": [
                "sport_alignment", "audience_match", "engagement_quality",
                "budget_fit", "location_proximity", "athlete_followers", "brand_budget"
            ],
            "success_prediction": [
                "budget", "duration_days", "athlete_followers", "engagement_rate",
                "brand_industry_match", "campaign_type_score"
            ],
            "value_estimation": [
                "athlete_followers", "engagement_rate", "sport_popularity",
                "brand_budget", "location_factor", "seasonality_factor"
            ]
        }
    
    async def prepare_training_data(self, model_type: str, days: int) -> List[Dict]:
        """Prepare training data for specified model type"""
        logger.info("Preparing training data", model_type=model_type, days=days)
        
        # In production, this would fetch real data from PocketBase
        # For now, generate realistic synthetic data
        
        if model_type == "compatibility":
            return self._generate_compatibility_data(days)
        elif model_type == "success_prediction":
            return self._generate_success_prediction_data(days)
        elif model_type == "value_estimation":
            return self._generate_value_estimation_data(days)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    async def prepare_evaluation_data(self, model_type: str, days: int) -> List[Dict]:
        """Prepare evaluation data (separate from training)"""
        # Generate smaller dataset for evaluation
        eval_days = min(days, 30)
        return await self.prepare_training_data(model_type, eval_days)
    
    def _generate_compatibility_data(self, days: int) -> List[Dict]:
        """Generate synthetic compatibility training data"""
        np.random.seed(42)  # For reproducible results
        
        data = []
        num_samples = days * 5  # 5 samples per day
        
        sports = ["basketball", "soccer", "tennis", "swimming", "football"]
        industries = ["sports_apparel", "fitness", "nutrition", "technology", "automotive"]
        
        for i in range(num_samples):
            # Generate realistic athlete data
            sport = np.random.choice(sports)
            followers = np.random.lognormal(9, 1)  # Log-normal distribution for followers
            engagement = np.random.beta(2, 8) * 15  # Beta distribution for engagement rate
            
            # Generate brand data
            industry = np.random.choice(industries)
            brand_budget = np.random.uniform(2000, 50000)
            
            # Calculate alignment factors
            sport_industry_match = self._calculate_sport_industry_match(sport, industry)
            budget_fit = self._calculate_budget_fit(followers, engagement, brand_budget)
            location_match = np.random.uniform(0.2, 1.0)
            
            # Calculate overall compatibility (ground truth)
            factors = {
                "sport_alignment": sport_industry_match,
                "audience_match": np.random.uniform(30, 95),
                "engagement_quality": min(100, engagement * 10),
                "budget_fit": budget_fit,
                "location_proximity": location_match * 100,
                "athlete_followers": followers,
                "brand_budget": brand_budget
            }
            
            # Weighted compatibility score
            compatibility_score = (
                factors["sport_alignment"] * 0.25 +
                factors["audience_match"] * 0.2 +
                factors["engagement_quality"] * 0.2 +
                factors["budget_fit"] * 0.15 +
                factors["location_proximity"] * 0.1 +
                min(100, np.log10(factors["athlete_followers"]) * 10) * 0.1
            )
            
            factors["compatibility_score"] = compatibility_score
            data.append(factors)
        
        logger.info("Compatibility data generated", samples=len(data))
        return data
    
    def _generate_success_prediction_data(self, days: int) -> List[Dict]:
        """Generate synthetic campaign success data"""
        np.random.seed(43)
        
        data = []
        num_samples = days * 3
        
        for i in range(num_samples):
            budget = np.random.uniform(3000, 100000)
            duration = np.random.randint(7, 120)
            followers = np.random.lognormal(10, 1)
            engagement = np.random.beta(2, 8) * 12
            
            # Success factors
            budget_adequacy = min(1.0, budget / 15000)  # Normalize budget
            duration_score = 1.0 - abs(duration - 30) / 60  # Optimal around 30 days
            reach_score = min(1.0, followers / 100000)
            engagement_score = min(1.0, engagement / 8)
            
            # Calculate success probability
            success_prob = (
                budget_adequacy * 0.3 +
                duration_score * 0.2 +
                reach_score * 0.25 + 
                engagement_score * 0.25
            )
            
            # Add noise and convert to binary
            success = 1 if (success_prob + np.random.normal(0, 0.1)) > 0.6 else 0
            
            sample = {
                "campaign_id": f"campaign_{i}",
                "budget": budget,
                "duration_days": duration,
                "athlete_followers": followers,
                "engagement_rate": engagement,
                "brand_industry_match": np.random.uniform(0.4, 1.0),
                "success": success,
                "success_probability": success_prob
            }
            
            data.append(sample)
        
        logger.info("Success prediction data generated", samples=len(data))
        return data
    
    def _generate_value_estimation_data(self, days: int) -> List[Dict]:
        """Generate synthetic deal value data"""
        np.random.seed(44)
        
        data = []
        num_samples = days * 4
        
        for i in range(num_samples):
            followers = np.random.lognormal(9.5, 1.2)
            engagement = np.random.beta(2, 6) * 12
            sport_popularity = np.random.uniform(0.6, 1.0)
            
            # Value estimation formula
            base_value = followers * 0.01  # $0.01 per follower
            engagement_multiplier = 1 + (engagement / 10)
            sport_multiplier = sport_popularity
            market_factor = np.random.uniform(0.8, 1.3)
            
            estimated_value = base_value * engagement_multiplier * sport_multiplier * market_factor
            
            # Add realistic bounds
            actual_value = max(500, min(200000, estimated_value * np.random.uniform(0.7, 1.4)))
            
            sample = {
                "deal_id": f"deal_{i}",
                "athlete_followers": followers,
                "engagement_rate": engagement,
                "sport_popularity": sport_popularity,
                "brand_budget": np.random.uniform(10000, 200000),
                "location_factor": np.random.uniform(0.8, 1.2),
                "seasonality_factor": np.random.uniform(0.9, 1.1),
                "actual_value": actual_value
            }
            
            data.append(sample)
        
        logger.info("Value estimation data generated", samples=len(data))
        return data
    
    def _calculate_sport_industry_match(self, sport: str, industry: str) -> float:
        """Calculate how well sport aligns with industry"""
        alignments = {
            ("basketball", "sports_apparel"): 95,
            ("basketball", "fitness"): 85,
            ("basketball", "nutrition"): 70,
            ("soccer", "sports_apparel"): 90,
            ("soccer", "fitness"): 80,
            ("tennis", "sports_apparel"): 85,
            ("tennis", "technology"): 65,
            ("swimming", "fitness"): 95,
            ("swimming", "nutrition"): 85,
        }
        
        return alignments.get((sport, industry), 50)
    
    def _calculate_budget_fit(self, followers: float, engagement: float, budget: float) -> float:
        """Calculate how well budget fits athlete's estimated value"""
        estimated_rate = followers * 0.01 * (1 + engagement / 10)
        
        if budget >= estimated_rate * 0.8 and budget <= estimated_rate * 1.5:
            return 90 + np.random.uniform(-10, 10)
        elif budget >= estimated_rate * 0.5:
            return 70 + np.random.uniform(-15, 15) 
        else:
            return 40 + np.random.uniform(-20, 20)
    
    def prepare_features_for_inference(self, model_type: str, input_data: Dict) -> np.ndarray:
        """Prepare features for model inference"""
        feature_cols = self.feature_columns[model_type]
        features = []
        
        for col in feature_cols:
            value = input_data.get(col, 0)
            # Apply same normalization as training
            if col in ["athlete_followers", "brand_budget"]:
                value = value / 1000  # Normalize large numbers
            features.append(value)
        
        return np.array([features])
    
    def validate_training_data(self, data: List[Dict], model_type: str) -> Dict[str, Any]:
        """Validate training data quality"""
        df = pd.DataFrame(data)
        
        validation_results = {
            "total_samples": len(df),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_samples": df.duplicated().sum(),
            "data_quality_score": 0
        }
        
        # Calculate data quality score
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        uniqueness = 1 - (df.duplicated().sum() / len(df))
        
        validation_results["data_quality_score"] = (completeness + uniqueness) / 2
        validation_results["recommendations"] = []
        
        if completeness < 0.95:
            validation_results["recommendations"].append("Address missing values before training")
        
        if uniqueness < 0.9:
            validation_results["recommendations"].append("Remove duplicate samples")
        
        if len(df) < 100:
            validation_results["recommendations"].append("Collect more training samples")
        
        return validation_results