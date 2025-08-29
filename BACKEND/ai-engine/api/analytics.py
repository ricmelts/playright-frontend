from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()
router = APIRouter()

class PredictionRequest(BaseModel):
    athlete_id: str
    brand_id: str
    campaign_budget: float
    campaign_duration_days: int
    campaign_type: str

class MarketAnalysisRequest(BaseModel):
    sport: Optional[str] = None
    industry: Optional[str] = None
    time_period_days: int = 90

@router.post("/predict-campaign-success")
async def predict_campaign_success(request: PredictionRequest):
    """Predict campaign success rate and key metrics using AI"""
    try:
        # Mock ML prediction model - in production this would use trained models
        base_success_rate = 65.0
        
        # Factors affecting success rate
        factors = {
            "budget_adequacy": min(100, (request.campaign_budget / 10000) * 50),
            "duration_optimization": min(100, max(20, 100 - abs(request.campaign_duration_days - 30) * 2)),
            "campaign_type_effectiveness": {
                "social_media": 85,
                "endorsement": 75,
                "event_appearance": 70,
                "content_creation": 80,
                "brand_ambassador": 90
            }.get(request.campaign_type, 60)
        }
        
        # Calculate weighted success prediction
        weights = {"budget_adequacy": 0.3, "duration_optimization": 0.2, "campaign_type_effectiveness": 0.5}
        weighted_score = sum(factors[factor] * weight for factor, weight in weights.items())
        
        predicted_success_rate = min(95, max(15, base_success_rate + (weighted_score - 70) * 0.5))
        
        # Performance predictions
        follower_impact = request.campaign_budget * 0.1  # Estimated follower growth
        engagement_boost = min(50, request.campaign_budget / 1000)  # Engagement increase %
        
        prediction = {
            "athlete_id": request.athlete_id,
            "brand_id": request.brand_id,
            "predicted_success_rate": round(predicted_success_rate, 1),
            "confidence_score": 78.5,
            "performance_predictions": {
                "estimated_reach": int(request.campaign_budget * 50),  # Reach per dollar
                "predicted_engagement_boost": round(engagement_boost, 1),
                "estimated_follower_growth": int(follower_impact),
                "predicted_roi": round((predicted_success_rate / 100) * 2.3, 2)  # ROI multiplier
            },
            "key_factors": factors,
            "recommendations": [
                f"Optimize campaign duration to {30} days for maximum impact",
                "Focus on authentic content integration for higher engagement",
                "Leverage athlete's peak posting times for better reach"
            ],
            "risk_assessment": "Medium" if predicted_success_rate > 60 else "High"
        }
        
        logger.info("Campaign success predicted", 
                   athlete_id=request.athlete_id,
                   brand_id=request.brand_id,
                   success_rate=predicted_success_rate)
        
        return prediction
        
    except Exception as e:
        logger.error("Campaign prediction failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to predict campaign success")

@router.post("/market-analysis")
async def generate_market_analysis(request: MarketAnalysisRequest):
    """Generate comprehensive AI-powered market analysis"""
    try:
        # Mock advanced market analysis - would use real ML models in production
        analysis = {
            "market_overview": {
                "sport": request.sport or "overall",
                "industry": request.industry or "all_industries",
                "analysis_period_days": request.time_period_days,
                "market_size_estimate": "$2.4M" if request.sport == "basketball" else "$1.8M",
                "growth_rate": "18.5%",
                "market_maturity": "emerging"
            },
            "competitive_landscape": {
                "market_concentration": "low",
                "top_competitors": [
                    {"name": "OpendorseAI", "market_share": 15},
                    {"name": "NIL Network", "market_share": 12},
                    {"name": "CollectiveConnect", "market_share": 8}
                ],
                "competitive_intensity": "moderate",
                "barriers_to_entry": "medium"
            },
            "pricing_analysis": {
                "average_deal_value": 8500,
                "median_deal_value": 5200,
                "price_trend": "increasing",
                "value_drivers": [
                    "Social media following size",
                    "Engagement rate quality", 
                    "Sport popularity",
                    "Geographic market size"
                ]
            },
            "opportunity_analysis": {
                "high_potential_segments": [
                    "Micro-influencers (1K-10K followers) in niche sports",
                    "Local business partnerships with regional athletes",
                    "Content creation campaigns vs traditional endorsements"
                ],
                "emerging_trends": [
                    "Video-first content strategy showing 40% higher engagement",
                    "Authentic storytelling outperforming product placement",
                    "Cross-platform campaigns generating 25% more reach"
                ],
                "market_gaps": [
                    "Underserved women's sports segments",
                    "International student athletes",
                    "Emerging sports like esports crossover"
                ]
            },
            "predictions": {
                "6_month_outlook": {
                    "market_growth": "+25%",
                    "average_deal_value": "+12%",
                    "athlete_participation": "+30%",
                    "brand_investment": "+40%"
                },
                "key_factors": [
                    "Continued NIL rule evolution",
                    "Increased brand awareness of athlete marketing ROI",
                    "Platform algorithm changes affecting organic reach"
                ]
            },
            "recommendations": {
                "for_athletes": [
                    "Diversify content across multiple platforms",
                    "Focus on engagement quality over follower count",
                    "Build authentic personal brand narrative"
                ],
                "for_brands": [
                    "Start with smaller, targeted campaigns to test effectiveness",
                    "Prioritize long-term partnerships over one-off deals",
                    "Invest in content creation support for athletes"
                ],
                "for_agents": [
                    "Develop expertise in emerging sports and platforms",
                    "Build regional market knowledge for better local partnerships",
                    "Focus on data-driven deal structuring"
                ]
            }
        }
        
        logger.info("Market analysis generated", 
                   sport=request.sport,
                   industry=request.industry,
                   period_days=request.time_period_days)
        
        return analysis
        
    except Exception as e:
        logger.error("Market analysis generation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate market analysis")

@router.get("/performance-benchmarks")
async def get_performance_benchmarks(sport: Optional[str] = Query(None)):
    """Get AI-calculated performance benchmarks by sport"""
    try:
        # Mock benchmarking data - would be calculated from historical data
        sport_benchmarks = {
            "basketball": {
                "avg_followers": 45000,
                "avg_engagement_rate": 6.8,
                "avg_deal_value": 12000,
                "top_platforms": ["instagram", "tiktok", "twitter"],
                "content_performance": {
                    "game_highlights": 9.2,
                    "training_content": 7.8,
                    "lifestyle_posts": 6.5,
                    "brand_integrations": 5.9
                }
            },
            "soccer": {
                "avg_followers": 38000,
                "avg_engagement_rate": 7.2,
                "avg_deal_value": 9500,
                "top_platforms": ["instagram", "tiktok"],
                "content_performance": {
                    "match_highlights": 8.9,
                    "skill_tutorials": 8.1,
                    "team_content": 6.8,
                    "brand_integrations": 6.2
                }
            },
            "tennis": {
                "avg_followers": 25000,
                "avg_engagement_rate": 5.9,
                "avg_deal_value": 7800,
                "top_platforms": ["instagram", "youtube"],
                "content_performance": {
                    "match_highlights": 7.5,
                    "training_sessions": 6.9,
                    "lifestyle_content": 6.1,
                    "brand_integrations": 5.4
                }
            }
        }
        
        if sport and sport.lower() in sport_benchmarks:
            benchmarks = sport_benchmarks[sport.lower()]
            benchmarks["sport"] = sport
        else:
            # Overall benchmarks (weighted average)
            all_sports = sport_benchmarks.values()
            benchmarks = {
                "sport": "overall",
                "avg_followers": int(np.mean([s["avg_followers"] for s in all_sports])),
                "avg_engagement_rate": round(np.mean([s["avg_engagement_rate"] for s in all_sports]), 1),
                "avg_deal_value": int(np.mean([s["avg_deal_value"] for s in all_sports])),
                "top_platforms": ["instagram", "tiktok", "twitter"],
                "content_performance": {
                    "sports_content": 8.1,
                    "lifestyle_content": 6.8,
                    "training_content": 7.5,
                    "brand_integrations": 5.9
                }
            }
        
        # Add percentile breakdowns
        benchmarks["percentile_breakdown"] = {
            "followers": {
                "25th_percentile": benchmarks["avg_followers"] * 0.4,
                "50th_percentile": benchmarks["avg_followers"] * 0.7,
                "75th_percentile": benchmarks["avg_followers"] * 1.3,
                "90th_percentile": benchmarks["avg_followers"] * 2.1
            },
            "engagement_rate": {
                "25th_percentile": benchmarks["avg_engagement_rate"] * 0.6,
                "50th_percentile": benchmarks["avg_engagement_rate"] * 0.9,
                "75th_percentile": benchmarks["avg_engagement_rate"] * 1.2,
                "90th_percentile": benchmarks["avg_engagement_rate"] * 1.6
            }
        }
        
        logger.info("Performance benchmarks retrieved", sport=sport)
        return benchmarks
        
    except Exception as e:
        logger.error("Failed to get performance benchmarks", sport=sport, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve performance benchmarks")

@router.post("/optimize-campaign")
async def optimize_campaign_strategy(campaign_data: Dict[str, Any]):
    """Generate AI-powered campaign optimization recommendations"""
    try:
        # Analyze campaign parameters
        budget = campaign_data.get("budget", 0)
        target_sports = campaign_data.get("target_sports", [])
        duration_days = campaign_data.get("duration_days", 30)
        campaign_type = campaign_data.get("campaign_type", "endorsement")
        
        optimizations = {
            "budget_allocation": {
                "recommended_split": {
                    "athlete_compensation": 60,
                    "content_production": 25,
                    "promotion_boost": 15
                },
                "explanation": "Optimal allocation based on similar successful campaigns"
            },
            "timing_optimization": {
                "optimal_duration": self._calculate_optimal_duration(budget, campaign_type),
                "best_launch_timing": "Tuesday-Thursday for maximum initial engagement",
                "content_frequency": "3-4 posts per week for sustained engagement"
            },
            "athlete_selection": {
                "recommended_tier": "micro-influencer" if budget < 5000 else "mid-tier" if budget < 20000 else "macro-influencer",
                "optimal_follower_range": self._get_optimal_follower_range(budget),
                "engagement_threshold": "minimum 4.5% engagement rate"
            },
            "content_strategy": {
                "recommended_content_mix": {
                    "authentic_integration": 40,
                    "product_showcase": 30,
                    "behind_scenes": 20,
                    "user_generated_content": 10
                },
                "platform_strategy": self._get_platform_strategy(target_sports, budget)
            },
            "success_metrics": {
                "primary_kpis": ["engagement_rate", "reach", "brand_awareness_lift"],
                "tracking_recommendations": [
                    "Use unique campaign hashtags for attribution",
                    "Implement UTM parameters for traffic tracking",
                    "Set up conversion pixel for purchase attribution"
                ]
            }
        }
        
        # Calculate expected ROI
        expected_roi = self._predict_campaign_roi(budget, campaign_type, target_sports)
        optimizations["roi_prediction"] = {
            "expected_roi": round(expected_roi, 2),
            "confidence_interval": [round(expected_roi * 0.7, 2), round(expected_roi * 1.3, 2)],
            "payback_period_days": max(30, min(180, int(budget / (expected_roi * 100))))
        }
        
        logger.info("Campaign optimization generated", 
                   budget=budget,
                   sports=target_sports,
                   expected_roi=expected_roi)
        
        return optimizations
        
    except Exception as e:
        logger.error("Campaign optimization failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to optimize campaign strategy")

def _calculate_optimal_duration(self, budget: float, campaign_type: str) -> int:
    """Calculate optimal campaign duration based on budget and type"""
    base_duration = {
        "social_media": 21,
        "endorsement": 45,
        "event_appearance": 7,
        "content_creation": 30,
        "brand_ambassador": 90
    }.get(campaign_type, 30)
    
    # Adjust based on budget
    if budget > 20000:
        return base_duration + 14  # Longer campaigns for bigger budgets
    elif budget < 5000:
        return max(7, base_duration - 14)  # Shorter for smaller budgets
    
    return base_duration

def _get_optimal_follower_range(self, budget: float) -> Dict[str, int]:
    """Get optimal follower range based on budget"""
    if budget < 2000:
        return {"min": 1000, "max": 10000}
    elif budget < 5000:
        return {"min": 5000, "max": 25000}
    elif budget < 15000:
        return {"min": 15000, "max": 75000}
    elif budget < 50000:
        return {"min": 50000, "max": 200000}
    else:
        return {"min": 100000, "max": 1000000}

def _get_platform_strategy(self, sports: List[str], budget: float) -> Dict[str, Any]:
    """Get platform-specific strategy recommendations"""
    strategies = {
        "basketball": {
            "primary": "instagram",
            "secondary": ["tiktok", "twitter"],
            "content_focus": "game highlights and training content"
        },
        "soccer": {
            "primary": "tiktok",
            "secondary": ["instagram", "youtube"],
            "content_focus": "skill demonstrations and match content"
        },
        "tennis": {
            "primary": "instagram", 
            "secondary": ["youtube", "twitter"],
            "content_focus": "technique videos and tournament updates"
        }
    }
    
    if not sports:
        return {
            "primary": "instagram",
            "secondary": ["tiktok"],
            "content_focus": "sport-specific authentic content",
            "budget_allocation": {"instagram": 60, "tiktok": 40}
        }
    
    sport = sports[0].lower()
    strategy = strategies.get(sport, strategies["basketball"])  # Default to basketball
    
    # Budget-based platform allocation
    if budget < 5000:
        strategy["budget_allocation"] = {strategy["primary"]: 100}
    elif budget < 15000:
        strategy["budget_allocation"] = {strategy["primary"]: 70, strategy["secondary"][0]: 30}
    else:
        strategy["budget_allocation"] = {
            strategy["primary"]: 50,
            strategy["secondary"][0]: 30,
            strategy["secondary"][1]: 20
        }
    
    return strategy

def _predict_campaign_roi(self, budget: float, campaign_type: str, sports: List[str]) -> float:
    """Predict campaign ROI based on historical data patterns"""
    base_roi = {
        "social_media": 2.1,
        "endorsement": 1.8,
        "event_appearance": 1.5,
        "content_creation": 2.3,
        "brand_ambassador": 2.7
    }.get(campaign_type, 2.0)
    
    # Sport multipliers
    sport_multipliers = {
        "basketball": 1.2,
        "soccer": 1.1,
        "football": 1.15,
        "tennis": 0.95,
        "swimming": 0.9
    }
    
    sport_factor = 1.0
    if sports:
        sport_factor = sport_multipliers.get(sports[0].lower(), 1.0)
    
    # Budget efficiency curve (diminishing returns)
    if budget > 50000:
        budget_factor = 0.85
    elif budget > 20000:
        budget_factor = 0.95
    elif budget < 2000:
        budget_factor = 0.8  # Very small budgets less efficient
    else:
        budget_factor = 1.0
    
    return base_roi * sport_factor * budget_factor