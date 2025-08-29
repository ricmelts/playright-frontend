from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
import structlog

from app.core.pocketbase import pb_client

logger = structlog.get_logger()
router = APIRouter()

class BrandCreate(BaseModel):
    company_name: str
    industry: str
    location: str
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    target_demographics: Optional[Dict[str, Any]] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_sports: Optional[List[str]] = None

class BrandUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    target_demographics: Optional[Dict[str, Any]] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_sports: Optional[List[str]] = None

@router.get("/")
async def get_brands(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    industry: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    verified: Optional[bool] = Query(None),
    min_budget: Optional[float] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get paginated list of brands with optional filters"""
    try:
        filters = {}
        if industry:
            filters["industry"] = industry
        if verified is not None:
            filters["verified"] = verified
        if min_budget:
            filters["budget_min"] = min_budget
        if search:
            filters["search"] = search
        
        result = pb_client.get_brands(filters, page, per_page)
        
        logger.info("Brands retrieved", count=len(result["items"]), page=page)
        return result
        
    except Exception as e:
        logger.error("Failed to get brands", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve brands")

@router.get("/{brand_id}")
async def get_brand(brand_id: str):
    """Get specific brand by ID with full profile data"""
    try:
        brand = pb_client.client.collection("brands").get_one(
            brand_id, 
            expand="user"
        )
        
        # Get active campaigns
        campaigns = pb_client.client.collection("campaigns").get_list(
            filter=f"brand = '{brand_id}'",
            sort="-created",
            per_page=5
        )
        
        # Get recent deals
        deals = pb_client.client.collection("deals").get_list(
            filter=f"brand = '{brand_id}'",
            sort="-created",
            per_page=5,
            expand="athlete"
        )
        
        brand_data = brand.to_dict()
        brand_data["campaigns"] = [c.to_dict() for c in campaigns.items]
        brand_data["recent_deals"] = [d.to_dict() for d in deals.items]
        
        logger.info("Brand retrieved", brand_id=brand_id)
        return brand_data
        
    except Exception as e:
        logger.error("Failed to get brand", brand_id=brand_id, error=str(e))
        raise HTTPException(status_code=404, detail="Brand not found")

@router.post("/")
async def create_brand(brand_data: BrandCreate):
    """Create new brand profile"""
    try:
        # Ensure user has brand role
        current_user = pb_client.client.auth_store.model
        if not current_user or current_user.role != "brand":
            raise HTTPException(status_code=403, detail="Only users with brand role can create brand profiles")
        
        # Create brand record
        brand_record = pb_client.client.collection("brands").create({
            "user": current_user.id,
            **brand_data.dict()
        })
        
        # Mark user profile as completed
        pb_client.client.collection("users").update(current_user.id, {
            "profile_completed": True
        })
        
        logger.info("Brand profile created", brand_id=brand_record.id, user_id=current_user.id)
        return brand_record.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create brand", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create brand profile")

@router.patch("/{brand_id}")
async def update_brand(brand_id: str, update_data: BrandUpdate):
    """Update brand profile"""
    try:
        # Verify ownership or admin access
        current_user = pb_client.client.auth_store.model
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        brand = pb_client.client.collection("brands").get_one(brand_id)
        if brand.user != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this profile")
        
        # Update brand record
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        updated_brand = pb_client.client.collection("brands").update(brand_id, update_dict)
        
        logger.info("Brand profile updated", brand_id=brand_id)
        return updated_brand.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update brand", brand_id=brand_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update brand profile")

@router.post("/{brand_id}/upload-logo")
async def upload_brand_logo(brand_id: str, file: UploadFile = File(...)):
    """Upload logo for brand"""
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="File must be an image (JPEG, PNG, WebP, or SVG)")
        
        # Upload to PocketBase
        brand = pb_client.client.collection("brands").update(brand_id, {
            "logo": file.file
        })
        
        logger.info("Brand logo uploaded", brand_id=brand_id, filename=file.filename)
        return {"message": "Logo uploaded successfully", "logo_url": brand.logo}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to upload logo", brand_id=brand_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload logo")

@router.get("/{brand_id}/campaigns")
async def get_brand_campaigns(
    brand_id: str,
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50)
):
    """Get campaigns for specific brand"""
    try:
        filter_parts = [f"brand = '{brand_id}'"]
        if status:
            filter_parts.append(f"status = '{status}'")
        
        filter_string = " && ".join(filter_parts)
        
        campaigns = pb_client.client.collection("campaigns").get_list(
            filter=filter_string,
            page=page,
            per_page=per_page,
            sort="-created"
        )
        
        result = {
            "items": [c.to_dict() for c in campaigns.items],
            "total_items": campaigns.total_items,
            "total_pages": campaigns.total_pages,
            "page": campaigns.page,
            "per_page": campaigns.per_page
        }
        
        logger.info("Brand campaigns retrieved", brand_id=brand_id, count=len(result["items"]))
        return result
        
    except Exception as e:
        logger.error("Failed to get brand campaigns", brand_id=brand_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve brand campaigns")

@router.get("/{brand_id}/deals")
async def get_brand_deals(
    brand_id: str,
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50)
):
    """Get deals for specific brand"""
    try:
        filters = {"brand_id": brand_id}
        if status:
            filters["status"] = status
        
        deals = pb_client.get_deals(filters, page, per_page)
        
        logger.info("Brand deals retrieved", brand_id=brand_id, count=len(deals["items"]))
        return deals
        
    except Exception as e:
        logger.error("Failed to get brand deals", brand_id=brand_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve brand deals")

@router.get("/{brand_id}/analytics")
async def get_brand_analytics(brand_id: str, days: int = Query(30, ge=1, le=365)):
    """Get brand performance analytics"""
    try:
        # This would integrate with analytics service
        # For now, return placeholder data
        analytics = {
            "total_deals": 0,
            "total_spent": 0,
            "avg_deal_value": 0,
            "success_rate": 0,
            "top_sports": [],
            "performance_trend": []
        }
        
        # Get actual data from deals
        deals = pb_client.client.collection("deals").get_list(
            filter=f"brand = '{brand_id}'",
            per_page=500,  # Get all deals
            expand="athlete"
        )
        
        if deals.items:
            deal_values = [d.value for d in deals.items if d.value]
            analytics["total_deals"] = len(deals.items)
            analytics["total_spent"] = sum(deal_values)
            analytics["avg_deal_value"] = sum(deal_values) / len(deal_values) if deal_values else 0
            
            # Calculate success rate
            completed_deals = [d for d in deals.items if d.status == "completed"]
            analytics["success_rate"] = (len(completed_deals) / len(deals.items)) * 100 if deals.items else 0
            
            # Top sports
            sports_count = {}
            for deal in deals.items:
                if hasattr(deal, 'expand') and deal.expand.get('athlete'):
                    sport = deal.expand['athlete'].sport
                    sports_count[sport] = sports_count.get(sport, 0) + 1
            analytics["top_sports"] = sorted(sports_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        logger.info("Brand analytics retrieved", brand_id=brand_id)
        return analytics
        
    except Exception as e:
        logger.error("Failed to get brand analytics", brand_id=brand_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve brand analytics")