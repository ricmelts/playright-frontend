from pydantic import validator, EmailStr
from typing import Dict, List, Any, Optional
import re
from datetime import datetime, date
import structlog

logger = structlog.get_logger()

class ValidationUtils:
    """Utility functions for data validation"""
    
    @staticmethod
    def validate_social_media_username(platform: str, username: str) -> bool:
        """Validate social media username format"""
        patterns = {
            "instagram": r"^[a-zA-Z0-9._]{1,30}$",
            "tiktok": r"^[a-zA-Z0-9._]{1,24}$", 
            "twitter": r"^[a-zA-Z0-9_]{1,15}$",
            "youtube": r"^[a-zA-Z0-9_-]{3,30}$"
        }
        
        pattern = patterns.get(platform.lower())
        if not pattern:
            return False
        
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_nil_eligibility(graduation_year: Optional[int], sport: str) -> bool:
        """Validate NIL eligibility based on graduation year and sport"""
        if not graduation_year:
            return True  # Allow manual verification
        
        current_year = datetime.now().year
        
        # Must be currently enrolled (not graduated more than 1 year ago)
        if graduation_year < current_year - 1:
            return False
        
        # Must not be graduated more than 4 years in future
        if graduation_year > current_year + 4:
            return False
        
        return True
    
    @staticmethod
    def validate_budget_range(budget_min: Optional[float], budget_max: Optional[float]) -> bool:
        """Validate budget range makes sense"""
        if budget_min is None or budget_max is None:
            return True
        
        return budget_min <= budget_max and budget_min >= 0
    
    @staticmethod
    def validate_campaign_dates(start_date: date, end_date: date, deadline: Optional[date] = None) -> bool:
        """Validate campaign date logic"""
        current_date = datetime.now().date()
        
        # Start date must be in the future or today
        if start_date < current_date:
            return False
        
        # End date must be after start date
        if end_date <= start_date:
            return False
        
        # Deadline should be before or on start date
        if deadline and deadline > start_date:
            return False
        
        return True
    
    @staticmethod
    def validate_deal_value(value: float, athlete_metrics: List[Dict] = None) -> bool:
        """Validate deal value is reasonable"""
        if value <= 0:
            return False
        
        # Basic sanity check - deals shouldn't exceed $1M for college athletes
        if value > 1000000:
            return False
        
        # If metrics available, check if value is reasonable for follower count
        if athlete_metrics:
            total_followers = sum(m.get("followers", 0) for m in athlete_metrics)
            # Very rough rule: shouldn't exceed $1 per follower for most deals
            if total_followers > 0 and value > total_followers:
                logger.warning("Deal value may be high relative to follower count",
                             value=value, followers=total_followers)
        
        return True
    
    @staticmethod
    def sanitize_user_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user text input"""
        if not text:
            return ""
        
        # Remove potential harmful characters
        cleaned = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length].rsplit(' ', 1)[0] + '...'
        
        return cleaned.strip()
    
    @staticmethod
    def validate_social_media_data(social_data: Dict[str, str]) -> Dict[str, List[str]]:
        """Validate social media data and return errors"""
        errors = {"valid": [], "invalid": []}
        
        supported_platforms = ["instagram", "tiktok", "twitter", "youtube"]
        
        for platform, username in social_data.items():
            if platform.lower() not in supported_platforms:
                errors["invalid"].append(f"Platform '{platform}' not supported")
                continue
            
            if not ValidationUtils.validate_social_media_username(platform, username):
                errors["invalid"].append(f"Invalid username format for {platform}: '{username}'")
                continue
            
            errors["valid"].append(f"{platform}: {username}")
        
        return errors

class AthleteValidator:
    """Validator for athlete-specific data"""
    
    @staticmethod
    def validate_sport(sport: str) -> bool:
        """Validate sport is supported"""
        supported_sports = [
            "basketball", "soccer", "tennis", "swimming", "football", 
            "baseball", "golf", "track", "volleyball", "softball",
            "wrestling", "gymnastics", "cross_country", "lacrosse", "other"
        ]
        return sport.lower() in supported_sports
    
    @staticmethod
    def validate_athlete_profile(data: Dict[str, Any]) -> List[str]:
        """Comprehensive athlete profile validation"""
        errors = []
        
        # Required fields
        required_fields = ["first_name", "last_name", "sport", "school"]
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Sport validation
        sport = data.get("sport", "")
        if sport and not AthleteValidator.validate_sport(sport):
            errors.append(f"Unsupported sport: {sport}")
        
        # NIL eligibility check
        graduation_year = data.get("graduation_year")
        if graduation_year and not ValidationUtils.validate_nil_eligibility(graduation_year, sport):
            errors.append("Invalid graduation year for NIL eligibility")
        
        # Social media validation
        social_media = data.get("social_media", {})
        if social_media:
            social_errors = ValidationUtils.validate_social_media_data(social_media)
            errors.extend(social_errors["invalid"])
        
        return errors

class BrandValidator:
    """Validator for brand-specific data"""
    
    @staticmethod
    def validate_industry(industry: str) -> bool:
        """Validate industry is supported"""
        supported_industries = [
            "sports_apparel", "fitness", "nutrition", "technology", 
            "automotive", "food_beverage", "retail", "financial", 
            "healthcare", "education", "entertainment", "other"
        ]
        return industry.lower() in supported_industries
    
    @staticmethod
    def validate_brand_profile(data: Dict[str, Any]) -> List[str]:
        """Comprehensive brand profile validation"""
        errors = []
        
        # Required fields
        required_fields = ["company_name", "industry", "location"]
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Industry validation
        industry = data.get("industry", "")
        if industry and not BrandValidator.validate_industry(industry):
            errors.append(f"Unsupported industry: {industry}")
        
        # Budget validation
        budget_min = data.get("budget_min")
        budget_max = data.get("budget_max")
        if not ValidationUtils.validate_budget_range(budget_min, budget_max):
            errors.append("Invalid budget range: minimum must be less than or equal to maximum")
        
        # Website URL validation (basic)
        website = data.get("website")
        if website and not website.startswith(("http://", "https://")):
            errors.append("Website URL must start with http:// or https://")
        
        return errors

class DealValidator:
    """Validator for deal-specific data"""
    
    @staticmethod
    def validate_deal_data(data: Dict[str, Any], athlete_metrics: List[Dict] = None) -> List[str]:
        """Comprehensive deal validation"""
        errors = []
        
        # Required fields
        required_fields = ["athlete_id", "brand_id", "title", "value", "contract_type"]
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Value validation
        value = data.get("value", 0)
        if not ValidationUtils.validate_deal_value(value, athlete_metrics):
            errors.append("Invalid deal value")
        
        # Date validation
        start_date = data.get("start_date")
        end_date = data.get("end_date") 
        deadline = data.get("deadline")
        
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date).date() if isinstance(start_date, str) else start_date
                end = datetime.fromisoformat(end_date).date() if isinstance(end_date, str) else end_date
                dead = datetime.fromisoformat(deadline).date() if isinstance(deadline, str) and deadline else None
                
                if not ValidationUtils.validate_campaign_dates(start, end, dead):
                    errors.append("Invalid date configuration")
            except (ValueError, TypeError):
                errors.append("Invalid date format")
        
        # Contract type validation
        contract_type = data.get("contract_type", "")
        valid_types = ["endorsement", "sponsorship", "appearance", "social_media", "licensing", "other"]
        if contract_type and contract_type not in valid_types:
            errors.append(f"Invalid contract type: {contract_type}")
        
        return errors

class CampaignValidator:
    """Validator for campaign-specific data"""
    
    @staticmethod
    def validate_campaign_data(data: Dict[str, Any]) -> List[str]:
        """Comprehensive campaign validation"""
        errors = []
        
        # Required fields
        required_fields = ["title", "budget", "target_sports", "start_date", "end_date"]
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Budget validation
        budget = data.get("budget", 0)
        if budget <= 0:
            errors.append("Budget must be greater than 0")
        
        # Target sports validation
        target_sports = data.get("target_sports", [])
        if not isinstance(target_sports, list) or not target_sports:
            errors.append("At least one target sport must be specified")
        else:
            for sport in target_sports:
                if not AthleteValidator.validate_sport(sport):
                    errors.append(f"Unsupported target sport: {sport}")
        
        # Date validation
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        deadline = data.get("application_deadline")
        
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date).date() if isinstance(start_date, str) else start_date
                end = datetime.fromisoformat(end_date).date() if isinstance(end_date, str) else end_date
                dead = datetime.fromisoformat(deadline).date() if isinstance(deadline, str) and deadline else None
                
                if not ValidationUtils.validate_campaign_dates(start, end, dead):
                    errors.append("Invalid campaign date configuration")
            except (ValueError, TypeError):
                errors.append("Invalid date format")
        
        # Campaign type validation
        campaign_type = data.get("campaign_type", "")
        valid_types = ["social_media", "event_appearance", "product_endorsement", "content_creation", "brand_ambassador", "other"]
        if campaign_type and campaign_type not in valid_types:
            errors.append(f"Invalid campaign type: {campaign_type}")
        
        return errors

# Decorator for automatic validation
def validate_request(validator_class, method_name):
    """Decorator to automatically validate request data"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract data from request
            data = kwargs.get('data') or kwargs.get('request_data')
            if not data:
                # Try to find data in function arguments
                for arg in args[1:]:  # Skip 'self' argument
                    if hasattr(arg, 'dict'):
                        data = arg.dict()
                        break
            
            if data:
                validator = getattr(validator_class, method_name)
                validation_errors = validator(data)
                
                if validation_errors:
                    raise ValidationError(
                        message=f"Validation failed: {'; '.join(validation_errors)}"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator