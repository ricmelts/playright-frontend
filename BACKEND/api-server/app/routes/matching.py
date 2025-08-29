from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import structlog

from app.core.pocketbase import pb_client
from app.services.ai_matching import AIMatchingService
from app.models.matching import MatchRequest, MatchResponse, MatchScore

logger = structlog.get_logger()
router = APIRouter()
ai_service = AIMatchingService()

class AthleteMatchRequest(BaseModel):
    brand_id: str
    sport_filter: Optional[str] = None
    min_followers: Optional[int] = None
    max_budget: Optional[int] = None
    location_preference: Optional[str] = None
    limit: int = 10

class BrandMatchRequest(BaseModel):
    athlete_id: str
    industry_preference: Optional[str] = None
    min_budget: Optional[int] = None
    campaign_type: Optional[str] = None
    limit: int = 10

@router.post("/athletes-for-brand", response_model=List[MatchResponse])
async def find_matching_athletes(request: AthleteMatchRequest):
    """Find athletes that match a brand's campaign requirements using AI"""
    try:
        # Get brand details
        brand = pb_client.client.collection("brands").get_one(request.brand_id, expand="user")
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Get all eligible athletes
        athletes_response = pb_client.get_athletes({
            "sport": request.sport_filter,
            "nil_eligible": True
        }, page=1, per_page=100)
        
        athletes = athletes_response["items"]
        
        # Filter by follower count if specified
        if request.min_followers:
            filtered_athletes = []
            for athlete in athletes:
                athlete_metrics = pb_client.client.collection("athlete_metrics").get_list(
                    filter=f"athlete = '{athlete['id']}'"
                )
                total_followers = sum(metric.get("followers", 0) for metric in athlete_metrics.items)
                if total_followers >= request.min_followers:
                    filtered_athletes.append(athlete)
            athletes = filtered_athletes
        
        # Use AI service to score and rank matches
        matches = await ai_service.find_athlete_matches(
            brand_data=brand.to_dict(),
            athletes_data=athletes,
            preferences={
                "max_budget": request.max_budget,
                "location_preference": request.location_preference
            }
        )
        
        # Limit results
        top_matches = matches[:request.limit]
        
        logger.info(
            "Athletes matched for brand",
            brand_id=request.brand_id,
            matches_found=len(top_matches)
        )
        
        return top_matches
        
    except Exception as e:
        logger.error("Error finding athlete matches", brand_id=request.brand_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to find matching athletes")

@router.post("/brands-for-athlete", response_model=List[MatchResponse])
async def find_matching_brands(request: BrandMatchRequest):
    """Find brands that match an athlete's profile and preferences using AI"""
    try:
        # Get athlete details
        athlete = pb_client.client.collection("athletes").get_one(request.athlete_id, expand="user")
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")
        
        # Get athlete's social media metrics
        metrics_response = pb_client.client.collection("athlete_metrics").get_list(
            filter=f"athlete = '{request.athlete_id}'"
        )
        
        # Get all verified brands
        brands_response = pb_client.get_brands({
            "verified": True,
            "industry": request.industry_preference
        }, page=1, per_page=100)
        
        brands = brands_response["items"]
        
        # Filter by budget if specified
        if request.min_budget:
            brands = [b for b in brands if b.get("budget_max", 0) >= request.min_budget]
        
        # Use AI service to score and rank matches
        matches = await ai_service.find_brand_matches(
            athlete_data=athlete.to_dict(),
            athlete_metrics=[m.to_dict() for m in metrics_response.items],
            brands_data=brands,
            preferences={
                "campaign_type": request.campaign_type
            }
        )
        
        # Limit results
        top_matches = matches[:request.limit]
        
        logger.info(
            "Brands matched for athlete",
            athlete_id=request.athlete_id,
            matches_found=len(top_matches)
        )
        
        return top_matches
        
    except Exception as e:
        logger.error("Error finding brand matches", athlete_id=request.athlete_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to find matching brands")

@router.get("/compatibility-score")
async def get_compatibility_score(
    athlete_id: str = Query(..., description="Athlete ID"),
    brand_id: str = Query(..., description="Brand ID")
):
    """Calculate detailed compatibility score between specific athlete and brand"""
    try:
        # Get athlete and brand data
        athlete = pb_client.client.collection("athletes").get_one(athlete_id, expand="user")
        brand = pb_client.client.collection("brands").get_one(brand_id, expand="user")
        
        if not athlete or not brand:
            raise HTTPException(status_code=404, detail="Athlete or brand not found")
        
        # Get athlete metrics
        metrics_response = pb_client.client.collection("athlete_metrics").get_list(
            filter=f"athlete = '{athlete_id}'"
        )
        
        # Calculate detailed compatibility
        compatibility = await ai_service.calculate_detailed_compatibility(
            athlete_data=athlete.to_dict(),
            athlete_metrics=[m.to_dict() for m in metrics_response.items],
            brand_data=brand.to_dict()
        )
        
        logger.info(
            "Compatibility score calculated",
            athlete_id=athlete_id,
            brand_id=brand_id,
            score=compatibility["overall_score"]
        )
        
        return compatibility
        
    except Exception as e:
        logger.error(
            "Error calculating compatibility score",
            athlete_id=athlete_id,
            brand_id=brand_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Failed to calculate compatibility score")

@router.post("/bulk-match")
async def bulk_match_analysis():
    """Run bulk AI matching analysis for all active campaigns"""
    try:
        await ai_service.run_bulk_matching_analysis()
        
        logger.info("Bulk matching analysis completed")
        return {"status": "success", "message": "Bulk matching analysis completed"}
        
    except Exception as e:
        logger.error("Bulk matching analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to run bulk matching analysis")

@router.get("/trending-athletes")
async def get_trending_athletes(
    sport: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """Get trending athletes based on recent engagement and growth"""
    try:
        trending = await ai_service.get_trending_athletes(sport=sport, limit=limit)
        
        logger.info("Trending athletes retrieved", sport=sport, count=len(trending))
        return trending
        
    except Exception as e:
        logger.error("Error getting trending athletes", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get trending athletes")