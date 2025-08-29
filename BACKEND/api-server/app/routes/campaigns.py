from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date
import structlog

from app.core.pocketbase import pb_client
from app.services.ai_matching import AIMatchingService

logger = structlog.get_logger()
router = APIRouter()
ai_service = AIMatchingService()

class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    budget: float
    target_sports: List[str]
    target_demographics: Optional[Dict[str, Any]] = None
    requirements: Optional[Dict[str, Any]] = None
    start_date: date
    end_date: date
    application_deadline: Optional[date] = None
    campaign_type: str = "endorsement"

class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    target_sports: Optional[List[str]] = None
    target_demographics: Optional[Dict[str, Any]] = None
    requirements: Optional[Dict[str, Any]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    application_deadline: Optional[date] = None
    status: Optional[str] = None
    campaign_type: Optional[str] = None

@router.get("/")
async def get_campaigns(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    brand_id: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    sport: Optional[str] = Query(None)
):
    """Get paginated list of campaigns with optional filters"""
    try:
        filter_parts = []
        
        if status:
            filter_parts.append(f"status = '{status}'")
        if brand_id:
            filter_parts.append(f"brand = '{brand_id}'")
        if campaign_type:
            filter_parts.append(f"campaign_type = '{campaign_type}'")
        
        filter_string = " && ".join(filter_parts) if filter_parts else ""
        
        campaigns = pb_client.client.collection("campaigns").get_list(
            page=page,
            per_page=per_page,
            filter=filter_string,
            expand="brand",
            sort="-created"
        )
        
        # Post-filter by sport if specified
        items = campaigns.items
        if sport:
            items = [c for c in items if sport in (c.target_sports or [])]
        
        result = {
            "items": [item.to_dict() for item in items],
            "total_items": campaigns.total_items,
            "total_pages": campaigns.total_pages,
            "page": campaigns.page,
            "per_page": campaigns.per_page
        }
        
        logger.info("Campaigns retrieved", count=len(result["items"]), page=page)
        return result
        
    except Exception as e:
        logger.error("Failed to get campaigns", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve campaigns")

@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get specific campaign by ID with full details"""
    try:
        campaign = pb_client.client.collection("campaigns").get_one(
            campaign_id, 
            expand="brand"
        )
        
        # Get related deals
        deals = pb_client.client.collection("deals").get_list(
            filter=f"brand = '{campaign.brand}' && created >= '{campaign.start_date}' && created <= '{campaign.end_date}'",
            expand="athlete",
            per_page=100
        )
        
        campaign_data = campaign.to_dict()
        campaign_data["related_deals"] = [d.to_dict() for d in deals.items]
        campaign_data["stats"] = {
            "total_applications": len(deals.items),
            "active_deals": len([d for d in deals.items if d.status == "active"]),
            "total_value": sum(d.value for d in deals.items if d.value)
        }
        
        logger.info("Campaign retrieved", campaign_id=campaign_id)
        return campaign_data
        
    except Exception as e:
        logger.error("Failed to get campaign", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=404, detail="Campaign not found")

@router.post("/")
async def create_campaign(campaign_data: CampaignCreate):
    """Create new campaign"""
    try:
        current_user = pb_client.client.auth_store.model
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get user's brand
        brand = pb_client.client.collection("brands").get_first_list_item(
            f"user = '{current_user.id}'"
        )
        
        if not brand:
            raise HTTPException(status_code=400, detail="Brand profile required to create campaigns")
        
        # Create campaign record
        campaign_record = pb_client.client.collection("campaigns").create({
            "brand": brand.id,
            "title": campaign_data.title,
            "description": campaign_data.description,
            "budget": campaign_data.budget,
            "target_sports": campaign_data.target_sports,
            "target_demographics": campaign_data.target_demographics,
            "requirements": campaign_data.requirements,
            "start_date": campaign_data.start_date.isoformat(),
            "end_date": campaign_data.end_date.isoformat(),
            "application_deadline": campaign_data.application_deadline.isoformat() if campaign_data.application_deadline else None,
            "campaign_type": campaign_data.campaign_type,
            "status": "active"
        })
        
        logger.info("Campaign created", campaign_id=campaign_record.id, brand_id=brand.id)
        return campaign_record.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create campaign", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create campaign")

@router.patch("/{campaign_id}")
async def update_campaign(campaign_id: str, update_data: CampaignUpdate):
    """Update campaign details"""
    try:
        # Verify ownership
        current_user = pb_client.client.auth_store.model
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        campaign = pb_client.client.collection("campaigns").get_one(campaign_id, expand="brand")
        if campaign.expand["brand"].user != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this campaign")
        
        # Update campaign
        update_dict = {}
        for key, value in update_data.dict().items():
            if value is not None:
                if isinstance(value, date):
                    update_dict[key] = value.isoformat()
                else:
                    update_dict[key] = value
        
        updated_campaign = pb_client.client.collection("campaigns").update(campaign_id, update_dict)
        
        logger.info("Campaign updated", campaign_id=campaign_id)
        return updated_campaign.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update campaign", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update campaign")

@router.post("/{campaign_id}/find-matches")
async def find_campaign_matches(
    campaign_id: str,
    limit: int = Query(20, ge=1, le=50),
    min_score: float = Query(70.0, ge=0, le=100)
):
    """Find AI-recommended athlete matches for campaign"""
    try:
        # Get campaign details
        campaign = pb_client.client.collection("campaigns").get_one(campaign_id, expand="brand")
        
        # Use AI service to find matches
        matches = await ai_service.find_athlete_matches(
            brand_data=campaign.expand["brand"].to_dict(),
            athletes_data=[],  # Will be fetched inside the service
            preferences={
                "target_sports": campaign.target_sports,
                "budget": campaign.budget,
                "requirements": campaign.requirements,
                "demographics": campaign.target_demographics
            }
        )
        
        # Filter by minimum score
        filtered_matches = [m for m in matches if m["overall_score"] >= min_score]
        
        # Limit results
        top_matches = filtered_matches[:limit]
        
        logger.info("Campaign matches found", 
                   campaign_id=campaign_id, 
                   total_matches=len(filtered_matches),
                   returned_matches=len(top_matches))
        
        return {
            "campaign_id": campaign_id,
            "matches": top_matches,
            "total_candidates": len(filtered_matches),
            "min_score_threshold": min_score
        }
        
    except Exception as e:
        logger.error("Failed to find campaign matches", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to find campaign matches")

@router.post("/{campaign_id}/upload-assets")
async def upload_campaign_assets(campaign_id: str, files: List[UploadFile] = File(...)):
    """Upload media assets for campaign"""
    try:
        # Validate file types
        allowed_types = [
            'image/jpeg', 'image/png', 'image/webp',
            'video/mp4', 'video/quicktime',
            'application/pdf'
        ]
        
        for file in files:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} type not allowed"
                )
        
        # Upload files to PocketBase
        campaign = pb_client.client.collection("campaigns").update(campaign_id, {
            "media_assets": [f.file for f in files]
        })
        
        filenames = [f.filename for f in files]
        logger.info("Campaign assets uploaded", campaign_id=campaign_id, files=filenames)
        
        return {
            "message": "Assets uploaded successfully",
            "files": filenames,
            "asset_urls": campaign.media_assets
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to upload campaign assets", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload assets")

@router.get("/{campaign_id}/analytics")
async def get_campaign_analytics(campaign_id: str):
    """Get campaign performance analytics"""
    try:
        campaign = pb_client.client.collection("campaigns").get_one(campaign_id)
        
        # Get all deals related to this campaign
        deals = pb_client.client.collection("deals").get_list(
            filter=f"brand = '{campaign.brand}' && created >= '{campaign.start_date}' && created <= '{campaign.end_date}'",
            expand="athlete",
            per_page=500
        )
        
        # Calculate analytics
        total_deals = len(deals.items)
        active_deals = len([d for d in deals.items if d.status in ["active", "negotiating", "pending_signatures"]])
        completed_deals = len([d for d in deals.items if d.status == "completed"])
        total_value = sum(d.value for d in deals.items if d.value)
        
        success_rate = (completed_deals / total_deals * 100) if total_deals > 0 else 0
        
        # Sports distribution
        sports_distribution = {}
        for deal in deals.items:
            if hasattr(deal, 'expand') and deal.expand.get('athlete'):
                sport = deal.expand['athlete'].sport
                sports_distribution[sport] = sports_distribution.get(sport, 0) + 1
        
        analytics = {
            "campaign_id": campaign_id,
            "total_deals": total_deals,
            "active_deals": active_deals,
            "completed_deals": completed_deals,
            "success_rate": round(success_rate, 2),
            "total_value": total_value,
            "avg_deal_value": total_value / total_deals if total_deals > 0 else 0,
            "sports_distribution": sports_distribution,
            "budget_utilization": (total_value / campaign.budget * 100) if campaign.budget > 0 else 0
        }
        
        logger.info("Campaign analytics retrieved", campaign_id=campaign_id)
        return analytics
        
    except Exception as e:
        logger.error("Failed to get campaign analytics", campaign_id=campaign_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve campaign analytics")