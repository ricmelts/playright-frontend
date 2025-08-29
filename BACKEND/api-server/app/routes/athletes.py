from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import structlog

from app.core.pocketbase import pb_client
from app.services.social_media import SocialMediaService

logger = structlog.get_logger()
router = APIRouter()
social_service = SocialMediaService()

class AthleteCreate(BaseModel):
    first_name: str
    last_name: str
    sport: str
    position: Optional[str] = None
    school: str
    location: str
    bio: Optional[str] = None
    nil_eligible: bool = True
    graduation_year: Optional[int] = None
    social_media: Optional[Dict[str, str]] = None

class AthleteUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sport: Optional[str] = None
    position: Optional[str] = None
    school: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    nil_eligible: Optional[bool] = None
    graduation_year: Optional[int] = None
    social_media: Optional[Dict[str, str]] = None

@router.get("/")
async def get_athletes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sport: Optional[str] = Query(None),
    school: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    nil_eligible: Optional[bool] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get paginated list of athletes with optional filters"""
    try:
        filters = {}
        if sport:
            filters["sport"] = sport
        if school:
            filters["school"] = school
        if nil_eligible is not None:
            filters["nil_eligible"] = nil_eligible
        
        # Add search functionality
        if search:
            filters["search"] = search
        
        result = pb_client.get_athletes(filters, page, per_page)
        
        logger.info("Athletes retrieved", count=len(result["items"]), page=page)
        return result
        
    except Exception as e:
        logger.error("Failed to get athletes", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve athletes")

@router.get("/{athlete_id}")
async def get_athlete(athlete_id: str):
    """Get specific athlete by ID with full profile data"""
    try:
        athlete = pb_client.client.collection("athletes").get_one(
            athlete_id, 
            expand="user"
        )
        
        # Get social media metrics
        metrics = pb_client.client.collection("athlete_metrics").get_list(
            filter=f"athlete = '{athlete_id}'",
            sort="-last_updated"
        )
        
        # Get recent deals
        deals = pb_client.client.collection("deals").get_list(
            filter=f"athlete = '{athlete_id}'",
            sort="-created",
            per_page=5,
            expand="brand"
        )
        
        athlete_data = athlete.to_dict()
        athlete_data["metrics"] = [m.to_dict() for m in metrics.items]
        athlete_data["recent_deals"] = [d.to_dict() for d in deals.items]
        
        logger.info("Athlete retrieved", athlete_id=athlete_id)
        return athlete_data
        
    except Exception as e:
        logger.error("Failed to get athlete", athlete_id=athlete_id, error=str(e))
        raise HTTPException(status_code=404, detail="Athlete not found")

@router.post("/")
async def create_athlete(athlete_data: AthleteCreate):
    """Create new athlete profile"""
    try:
        # First ensure user has athlete role
        current_user = pb_client.client.auth_store.model
        if not current_user or current_user.role != "athlete":
            raise HTTPException(status_code=403, detail="Only users with athlete role can create athlete profiles")
        
        # Create athlete record
        athlete_record = pb_client.client.collection("athletes").create({
            "user": current_user.id,
            **athlete_data.dict()
        })
        
        # If social media info provided, sync metrics
        if athlete_data.social_media:
            await social_service.sync_athlete_metrics(athlete_record.id, athlete_data.social_media)
        
        # Mark user profile as completed
        pb_client.client.collection("users").update(current_user.id, {
            "profile_completed": True
        })
        
        logger.info("Athlete profile created", athlete_id=athlete_record.id, user_id=current_user.id)
        return athlete_record.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create athlete", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create athlete profile")

@router.patch("/{athlete_id}")
async def update_athlete(athlete_id: str, update_data: AthleteUpdate):
    """Update athlete profile"""
    try:
        # Verify ownership or admin access
        current_user = pb_client.client.auth_store.model
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        athlete = pb_client.client.collection("athletes").get_one(athlete_id)
        if athlete.user != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this profile")
        
        # Update athlete record
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        updated_athlete = pb_client.client.collection("athletes").update(athlete_id, update_dict)
        
        # Update social media metrics if changed
        if update_data.social_media:
            await social_service.sync_athlete_metrics(athlete_id, update_data.social_media)
        
        logger.info("Athlete profile updated", athlete_id=athlete_id)
        return updated_athlete.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update athlete", athlete_id=athlete_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update athlete profile")

@router.post("/{athlete_id}/metrics/sync")
async def sync_athlete_metrics(athlete_id: str):
    """Sync athlete's social media metrics from external APIs"""
    try:
        # Get athlete with social media info
        athlete = pb_client.client.collection("athletes").get_one(athlete_id)
        social_media = athlete.social_media or {}
        
        if not social_media:
            raise HTTPException(status_code=400, detail="No social media accounts linked")
        
        # Sync metrics from external APIs
        updated_metrics = await social_service.sync_athlete_metrics(athlete_id, social_media)
        
        logger.info("Athlete metrics synced", athlete_id=athlete_id, platforms=list(social_media.keys()))
        return {"message": "Metrics synced successfully", "metrics": updated_metrics}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to sync metrics", athlete_id=athlete_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to sync social media metrics")

@router.get("/{athlete_id}/metrics")
async def get_athlete_metrics(athlete_id: str):
    """Get athlete's social media metrics history"""
    try:
        metrics = pb_client.client.collection("athlete_metrics").get_list(
            filter=f"athlete = '{athlete_id}'",
            sort="-last_updated"
        )
        
        logger.info("Athlete metrics retrieved", athlete_id=athlete_id, count=len(metrics.items))
        return [m.to_dict() for m in metrics.items]
        
    except Exception as e:
        logger.error("Failed to get athlete metrics", athlete_id=athlete_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@router.post("/{athlete_id}/upload-image")
async def upload_athlete_image(athlete_id: str, file: UploadFile = File(...)):
    """Upload profile image for athlete"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Upload to PocketBase
        athlete = pb_client.client.collection("athletes").update(athlete_id, {
            "profile_image": file.file
        })
        
        logger.info("Athlete image uploaded", athlete_id=athlete_id, filename=file.filename)
        return {"message": "Image uploaded successfully", "image_url": athlete.profile_image}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to upload image", athlete_id=athlete_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload image")

@router.get("/{athlete_id}/deals")
async def get_athlete_deals(
    athlete_id: str,
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50)
):
    """Get deals for specific athlete"""
    try:
        filters = {"athlete_id": athlete_id}
        if status:
            filters["status"] = status
        
        deals = pb_client.get_deals(filters, page, per_page)
        
        logger.info("Athlete deals retrieved", athlete_id=athlete_id, count=len(deals["items"]))
        return deals
        
    except Exception as e:
        logger.error("Failed to get athlete deals", athlete_id=athlete_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve athlete deals")