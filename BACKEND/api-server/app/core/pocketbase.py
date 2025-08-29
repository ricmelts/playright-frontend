from pocketbase import PocketBase
from pocketbase.client import ClientResponseError
import structlog
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = structlog.get_logger()

class PocketBaseClient:
    def __init__(self):
        self.client = PocketBase(settings.POCKETBASE_URL)
        self._admin_authenticated = False
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user for privileged operations"""
        try:
            if not self._admin_authenticated:
                self.client.admins.auth_with_password(
                    settings.POCKETBASE_ADMIN_EMAIL,
                    settings.POCKETBASE_ADMIN_PASSWORD
                )
                self._admin_authenticated = True
                logger.info("PocketBase admin authentication successful")
            return True
        except ClientResponseError as e:
            logger.error("PocketBase admin authentication failed", error=str(e))
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate a regular user"""
        try:
            auth_data = self.client.collection("users").auth_with_password(email, password)
            logger.info("User authentication successful", user_id=auth_data.record.id)
            return {
                "token": auth_data.token,
                "user": auth_data.record.to_dict(),
                "meta": auth_data.meta
            }
        except ClientResponseError as e:
            logger.error("User authentication failed", email=email, error=str(e))
            return None
    
    def create_user(self, email: str, password: str, role: str = "athlete", **kwargs) -> Optional[Dict]:
        """Create a new user"""
        try:
            user_data = {
                "email": email,
                "password": password,
                "passwordConfirm": password,
                "role": role,
                "verified": False,
                "profile_completed": False,
                **kwargs
            }
            
            record = self.client.collection("users").create(user_data)
            logger.info("User created successfully", user_id=record.id, email=email, role=role)
            return record.to_dict()
        except ClientResponseError as e:
            logger.error("User creation failed", email=email, error=str(e))
            return None
    
    def get_athletes(self, filters: Optional[Dict] = None, page: int = 1, per_page: int = 20) -> Dict:
        """Get athletes with optional filtering"""
        try:
            filter_string = ""
            if filters:
                filter_parts = []
                if filters.get("sport"):
                    filter_parts.append(f"sport = '{filters['sport']}'")
                if filters.get("school"):
                    filter_parts.append(f"school ~ '{filters['school']}'")
                if filters.get("nil_eligible"):
                    filter_parts.append("nil_eligible = true")
                filter_string = " && ".join(filter_parts)
            
            result = self.client.collection("athletes").get_list(
                page=page,
                per_page=per_page,
                filter=filter_string,
                expand="user"
            )
            
            return {
                "items": [item.to_dict() for item in result.items],
                "total_items": result.total_items,
                "total_pages": result.total_pages,
                "page": result.page,
                "per_page": result.per_page
            }
        except ClientResponseError as e:
            logger.error("Failed to get athletes", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to fetch athletes")
    
    def get_brands(self, filters: Optional[Dict] = None, page: int = 1, per_page: int = 20) -> Dict:
        """Get brands with optional filtering"""
        try:
            filter_string = ""
            if filters:
                filter_parts = []
                if filters.get("industry"):
                    filter_parts.append(f"industry = '{filters['industry']}'")
                if filters.get("verified"):
                    filter_parts.append("verified = true")
                if filters.get("budget_min"):
                    filter_parts.append(f"budget_max >= {filters['budget_min']}")
                filter_string = " && ".join(filter_parts)
            
            result = self.client.collection("brands").get_list(
                page=page,
                per_page=per_page,
                filter=filter_string,
                expand="user"
            )
            
            return {
                "items": [item.to_dict() for item in result.items],
                "total_items": result.total_items,
                "total_pages": result.total_pages,
                "page": result.page,
                "per_page": result.per_page
            }
        except ClientResponseError as e:
            logger.error("Failed to get brands", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to fetch brands")
    
    def get_deals(self, filters: Optional[Dict] = None, page: int = 1, per_page: int = 20) -> Dict:
        """Get deals with optional filtering"""
        try:
            filter_string = ""
            if filters:
                filter_parts = []
                if filters.get("status"):
                    filter_parts.append(f"status = '{filters['status']}'")
                if filters.get("athlete_id"):
                    filter_parts.append(f"athlete = '{filters['athlete_id']}'")
                if filters.get("brand_id"):
                    filter_parts.append(f"brand = '{filters['brand_id']}'")
                filter_string = " && ".join(filter_parts)
            
            result = self.client.collection("deals").get_list(
                page=page,
                per_page=per_page,
                filter=filter_string,
                expand="athlete,brand,agent",
                sort="-created"
            )
            
            return {
                "items": [item.to_dict() for item in result.items],
                "total_items": result.total_items,
                "total_pages": result.total_pages,
                "page": result.page,
                "per_page": result.per_page
            }
        except ClientResponseError as e:
            logger.error("Failed to get deals", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to fetch deals")
    
    def create_deal(self, deal_data: Dict) -> Optional[Dict]:
        """Create a new deal"""
        try:
            record = self.client.collection("deals").create(deal_data)
            logger.info("Deal created successfully", deal_id=record.id)
            return record.to_dict()
        except ClientResponseError as e:
            logger.error("Deal creation failed", error=str(e))
            return None
    
    def update_deal(self, deal_id: str, update_data: Dict) -> Optional[Dict]:
        """Update an existing deal"""
        try:
            record = self.client.collection("deals").update(deal_id, update_data)
            logger.info("Deal updated successfully", deal_id=deal_id)
            return record.to_dict()
        except ClientResponseError as e:
            logger.error("Deal update failed", deal_id=deal_id, error=str(e))
            return None


# Global PocketBase client instance
pb_client = PocketBaseClient()