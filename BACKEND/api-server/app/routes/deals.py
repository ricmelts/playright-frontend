from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import structlog

from app.core.pocketbase import pb_client
from app.services.ai_matching import AIMatchingService

logger = structlog.get_logger()
router = APIRouter()
ai_service = AIMatchingService()

class DealCreate(BaseModel):
    athlete_id: str
    brand_id: str
    title: str
    description: Optional[str] = None
    value: float
    contract_type: str = "endorsement"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    deadline: Optional[date] = None
    terms: Optional[Dict[str, Any]] = None
    deliverables: Optional[List[str]] = None

class DealUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    deadline: Optional[date] = None
    terms: Optional[Dict[str, Any]] = None
    deliverables: Optional[List[str]] = None
    progress: Optional[int] = None

class DealStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

@router.get("/")
async def get_deals(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    athlete_id: Optional[str] = Query(None),
    brand_id: Optional[str] = Query(None),
    contract_type: Optional[str] = Query(None),
    min_value: Optional[float] = Query(None),
    max_value: Optional[float] = Query(None)
):
    """Get paginated list of deals with optional filters"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if athlete_id:
            filters["athlete_id"] = athlete_id
        if brand_id:
            filters["brand_id"] = brand_id
        
        result = pb_client.get_deals(filters, page, per_page)
        
        # Add value filtering (post-query since PocketBase filter syntax is limited)
        if min_value is not None or max_value is not None:
            filtered_items = []
            for item in result["items"]:
                deal_value = item.get("value", 0)
                if min_value is not None and deal_value < min_value:
                    continue
                if max_value is not None and deal_value > max_value:
                    continue
                filtered_items.append(item)
            result["items"] = filtered_items
        
        logger.info("Deals retrieved", count=len(result["items"]), page=page)
        return result
        
    except Exception as e:
        logger.error("Failed to get deals", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve deals")

@router.get("/{deal_id}")
async def get_deal(deal_id: str):
    """Get specific deal by ID with full details"""
    try:
        deal = pb_client.client.collection("deals").get_one(
            deal_id, 
            expand="athlete,brand,agent"
        )
        
        deal_data = deal.to_dict()
        
        # Calculate AI compatibility score if not already present
        if not deal_data.get("ai_match_score"):
            try:
                athlete_id = deal_data["athlete"]
                brand_id = deal_data["brand"]
                
                # Get athlete metrics for scoring
                metrics = pb_client.client.collection("athlete_metrics").get_list(
                    filter=f"athlete = '{athlete_id}'"
                )
                
                compatibility = await ai_service.calculate_detailed_compatibility(
                    athlete_data=deal_data["expand"]["athlete"],
                    athlete_metrics=[m.to_dict() for m in metrics.items],
                    brand_data=deal_data["expand"]["brand"]
                )
                
                deal_data["ai_compatibility"] = compatibility
            except Exception as ai_error:
                logger.warning("Failed to calculate AI score for existing deal", 
                             deal_id=deal_id, error=str(ai_error))
        
        logger.info("Deal retrieved", deal_id=deal_id)
        return deal_data
        
    except Exception as e:
        logger.error("Failed to get deal", deal_id=deal_id, error=str(e))
        raise HTTPException(status_code=404, detail="Deal not found")

@router.post("/")
async def create_deal(deal_data: DealCreate):
    """Create new deal"""
    try:
        current_user = pb_client.client.auth_store.model
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Validate athlete and brand exist
        athlete = pb_client.client.collection("athletes").get_one(deal_data.athlete_id)
        brand = pb_client.client.collection("brands").get_one(deal_data.brand_id)
        
        # Calculate AI match score
        metrics = pb_client.client.collection("athlete_metrics").get_list(
            filter=f"athlete = '{deal_data.athlete_id}'"
        )
        
        compatibility = await ai_service.calculate_detailed_compatibility(
            athlete_data=athlete.to_dict(),
            athlete_metrics=[m.to_dict() for m in metrics.items],
            brand_data=brand.to_dict()
        )
        
        # Create deal with AI score
        deal_record = pb_client.client.collection("deals").create({
            "athlete": deal_data.athlete_id,
            "brand": deal_data.brand_id,
            "agent": current_user.id if current_user.role == "agent" else None,
            "title": deal_data.title,
            "description": deal_data.description,
            "value": deal_data.value,
            "contract_type": deal_data.contract_type,
            "start_date": deal_data.start_date.isoformat() if deal_data.start_date else None,
            "end_date": deal_data.end_date.isoformat() if deal_data.end_date else None,
            "deadline": deal_data.deadline.isoformat() if deal_data.deadline else None,
            "terms": deal_data.terms,
            "deliverables": deal_data.deliverables,
            "status": "proposed",
            "ai_match_score": compatibility["overall_score"]
        })
        
        logger.info("Deal created", deal_id=deal_record.id, athlete_id=deal_data.athlete_id, 
                   brand_id=deal_data.brand_id, value=deal_data.value)
        return deal_record.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create deal", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create deal")

@router.patch("/{deal_id}")
async def update_deal(deal_id: str, update_data: DealUpdate):
    """Update deal details"""
    try:
        # Get existing deal
        deal = pb_client.client.collection("deals").get_one(deal_id)
        
        # Check permissions
        current_user = pb_client.client.auth_store.model
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Update deal
        update_dict = {}
        for key, value in update_data.dict().items():
            if value is not None:
                if isinstance(value, date):
                    update_dict[key] = value.isoformat()
                else:
                    update_dict[key] = value
        
        updated_deal = pb_client.client.collection("deals").update(deal_id, update_dict)
        
        logger.info("Deal updated", deal_id=deal_id)
        return updated_deal.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update deal", deal_id=deal_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update deal")

@router.post("/{deal_id}/status")
async def update_deal_status(deal_id: str, status_data: DealStatusUpdate):
    """Update deal status with optional notes"""
    try:
        # Get existing deal
        deal = pb_client.client.collection("deals").get_one(deal_id)
        
        # Update status (this will trigger progress update via PocketBase hook)
        updated_deal = pb_client.client.collection("deals").update(deal_id, {
            "status": status_data.status
        })
        
        # Log status change with notes
        if status_data.notes:
            logger.info("Deal status updated with notes", 
                       deal_id=deal_id, 
                       old_status=deal.status, 
                       new_status=status_data.status,
                       notes=status_data.notes)
        
        logger.info("Deal status updated", deal_id=deal_id, status=status_data.status)
        return updated_deal.to_dict()
        
    except Exception as e:
        logger.error("Failed to update deal status", deal_id=deal_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update deal status")

@router.post("/{deal_id}/documents")
async def upload_deal_documents(deal_id: str, files: List[UploadFile] = File(...)):
    """Upload contract documents for deal"""
    try:
        # Validate file types
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        
        for file in files:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} must be PDF or Word document"
                )
        
        # Upload files to PocketBase
        deal = pb_client.client.collection("deals").update(deal_id, {
            "contract_documents": [f.file for f in files]
        })
        
        filenames = [f.filename for f in files]
        logger.info("Deal documents uploaded", deal_id=deal_id, files=filenames)
        return {
            "message": "Documents uploaded successfully", 
            "files": filenames,
            "document_urls": deal.contract_documents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to upload deal documents", deal_id=deal_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload documents")

@router.get("/{deal_id}/timeline")
async def get_deal_timeline(deal_id: str):
    """Get deal status change timeline"""
    try:
        # This would typically come from an audit log
        # For now, return basic timeline based on current status
        deal = pb_client.client.collection("deals").get_one(deal_id)
        
        timeline = [
            {
                "status": "proposed",
                "timestamp": deal.created,
                "description": "Deal proposed"
            }
        ]
        
        if deal.status != "proposed":
            timeline.append({
                "status": deal.status,
                "timestamp": deal.updated,
                "description": f"Status changed to {deal.status}"
            })
        
        logger.info("Deal timeline retrieved", deal_id=deal_id)
        return {"timeline": timeline}
        
    except Exception as e:
        logger.error("Failed to get deal timeline", deal_id=deal_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve deal timeline")