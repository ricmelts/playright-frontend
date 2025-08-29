from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MatchScore(BaseModel):
    overall_score: float = Field(..., ge=0, le=100, description="Overall compatibility score")
    semantic_similarity: float = Field(..., ge=0, le=100, description="AI semantic similarity score")
    sport_alignment: float = Field(..., ge=0, le=100, description="Sport compatibility score")
    location_proximity: float = Field(..., ge=0, le=100, description="Geographic proximity score")
    audience_demographics: float = Field(..., ge=0, le=100, description="Audience alignment score")
    budget_fit: float = Field(..., ge=0, le=100, description="Budget compatibility score")
    engagement_quality: float = Field(..., ge=0, le=100, description="Social media engagement score")
    brand_safety: float = Field(..., ge=0, le=100, description="Brand safety score")


class MatchRequest(BaseModel):
    entity_id: str = Field(..., description="ID of the entity to find matches for")
    entity_type: str = Field(..., description="Type of entity: 'athlete' or 'brand'")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional filtering criteria")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of matches to return")


class MatchResponse(BaseModel):
    match_id: str = Field(..., description="ID of the matched entity")
    name: str = Field(..., description="Name of the matched entity")
    type: str = Field(..., description="Type: 'athlete' or 'brand'")
    overall_score: float = Field(..., ge=0, le=100, description="Overall compatibility score")
    factors: MatchScore = Field(..., description="Detailed scoring factors")
    estimated_value: Optional[float] = Field(default=None, description="Estimated deal value")
    recommendation: str = Field(..., description="AI-generated recommendation")
    profile_summary: Dict[str, Any] = Field(..., description="Key profile information")
    last_updated: datetime = Field(default_factory=datetime.now)


class BulkMatchRequest(BaseModel):
    campaign_ids: Optional[List[str]] = Field(default=None, description="Specific campaigns to analyze")
    min_score_threshold: float = Field(default=70.0, ge=0, le=100, description="Minimum score threshold")
    update_existing: bool = Field(default=True, description="Whether to update existing match records")


class TrendingAthlete(BaseModel):
    athlete_id: str
    name: str
    sport: str
    school: Optional[str] = None
    total_followers: int
    engagement_rate: float
    trend_score: float = Field(..., description="Calculated trending score")
    growth_rate: Optional[float] = Field(default=None, description="Recent growth percentage")
    
    
class CompatibilityAnalysis(BaseModel):
    athlete_id: str
    brand_id: str
    overall_score: float = Field(..., ge=0, le=100)
    detailed_factors: MatchScore
    recommendation: str
    estimated_success_rate: float = Field(..., ge=0, le=100, description="Predicted campaign success rate")
    suggested_deal_value: Optional[float] = Field(default=None)
    risk_factors: List[str] = Field(default_factory=list, description="Potential risk factors")
    optimization_suggestions: List[str] = Field(default_factory=list, description="Ways to improve compatibility")


class MarketInsight(BaseModel):
    sport: str
    average_deal_value: float
    trending_athletes_count: int
    active_campaigns_count: int
    market_saturation: float = Field(..., ge=0, le=100, description="Market saturation percentage")
    growth_trend: str = Field(..., description="Market growth trend: 'rising', 'stable', 'declining'")
    top_industries: List[str] = Field(..., description="Most active industries in this sport")
    insights: List[str] = Field(..., description="AI-generated market insights")