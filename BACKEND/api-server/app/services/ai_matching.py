import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import structlog
import asyncio
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.pocketbase import pb_client

logger = structlog.get_logger()

class AIMatchingService:
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.DEFAULT_EMBEDDING_MODEL)
        self.match_threshold = settings.MATCHING_THRESHOLD
    
    def _create_athlete_profile_text(self, athlete_data: Dict, metrics: List[Dict]) -> str:
        """Create text representation of athlete for embedding"""
        sport = athlete_data.get("sport", "")
        school = athlete_data.get("school", "")
        location = athlete_data.get("location", "")
        bio = athlete_data.get("bio", "")
        
        # Aggregate social media metrics
        total_followers = sum(m.get("followers", 0) for m in metrics)
        avg_engagement = np.mean([m.get("engagement_rate", 0) for m in metrics]) if metrics else 0
        
        profile_text = f"""
        Athlete Profile:
        Sport: {sport}
        School: {school}
        Location: {location}
        Bio: {bio}
        Social Media: {total_followers} followers, {avg_engagement:.1f}% engagement
        """
        
        return profile_text.strip()
    
    def _create_brand_profile_text(self, brand_data: Dict) -> str:
        """Create text representation of brand for embedding"""
        company_name = brand_data.get("company_name", "")
        industry = brand_data.get("industry", "")
        description = brand_data.get("description", "")
        location = brand_data.get("location", "")
        preferred_sports = brand_data.get("preferred_sports", [])
        target_demographics = brand_data.get("target_demographics", {})
        
        profile_text = f"""
        Brand Profile:
        Company: {company_name}
        Industry: {industry}
        Description: {description}
        Location: {location}
        Preferred Sports: {', '.join(preferred_sports)}
        Target Demographics: {str(target_demographics)}
        """
        
        return profile_text.strip()
    
    def _calculate_compatibility_factors(self, athlete_data: Dict, brand_data: Dict, athlete_metrics: List[Dict]) -> Dict:
        """Calculate detailed compatibility factors"""
        factors = {
            "sport_alignment": 0,
            "location_proximity": 0,
            "audience_demographics": 0,
            "budget_fit": 0,
            "engagement_quality": 0,
            "brand_safety": 0
        }
        
        # Sport alignment
        athlete_sport = athlete_data.get("sport", "")
        brand_sports = brand_data.get("preferred_sports", [])
        if athlete_sport in brand_sports or not brand_sports:
            factors["sport_alignment"] = 100
        elif any(sport in athlete_sport.lower() for sport in brand_sports):
            factors["sport_alignment"] = 70
        else:
            factors["sport_alignment"] = 20
        
        # Location proximity
        athlete_location = athlete_data.get("location", "").lower()
        brand_location = brand_data.get("location", "").lower()
        if athlete_location == brand_location:
            factors["location_proximity"] = 100
        elif any(word in brand_location for word in athlete_location.split()):
            factors["location_proximity"] = 60
        else:
            factors["location_proximity"] = 30
        
        # Engagement quality
        if athlete_metrics:
            avg_engagement = np.mean([m.get("engagement_rate", 0) for m in athlete_metrics])
            if avg_engagement >= 8:
                factors["engagement_quality"] = 100
            elif avg_engagement >= 5:
                factors["engagement_quality"] = 80
            elif avg_engagement >= 2:
                factors["engagement_quality"] = 60
            else:
                factors["engagement_quality"] = 30
        
        # Budget fit (estimated based on follower count and engagement)
        total_followers = sum(m.get("followers", 0) for m in athlete_metrics)
        estimated_rate = self._estimate_athlete_rate(total_followers, factors["engagement_quality"])
        brand_budget_max = brand_data.get("budget_max", 0)
        
        if brand_budget_max > 0:
            if estimated_rate <= brand_budget_max * 0.8:
                factors["budget_fit"] = 100
            elif estimated_rate <= brand_budget_max:
                factors["budget_fit"] = 80
            elif estimated_rate <= brand_budget_max * 1.2:
                factors["budget_fit"] = 50
            else:
                factors["budget_fit"] = 20
        else:
            factors["budget_fit"] = 70  # Default if no budget specified
        
        # Audience demographics matching
        factors["audience_demographics"] = self._calculate_audience_demographics_score(athlete_data, brand_data, athlete_metrics)
        
        # Brand safety scoring
        factors["brand_safety"] = self._calculate_brand_safety_score(athlete_data, athlete_metrics)
        
        return factors
    
    def _calculate_audience_demographics_score(self, athlete_data: Dict, brand_data: Dict, athlete_metrics: List[Dict]) -> float:
        """Calculate audience demographics compatibility score"""
        score = 0
        total_weight = 0
        
        # Get brand's target demographics
        target_demographics = brand_data.get("target_demographics", {})
        
        if not target_demographics:
            return 70  # Default score if no target demographics specified
        
        # Age group matching
        if "age_group" in target_demographics and athlete_metrics:
            target_age_group = target_demographics["age_group"]
            athlete_age = athlete_data.get("age", 25)  # Default age if not specified
            
            # Map age to age groups
            if athlete_age <= 18:
                athlete_age_group = "under_18"
            elif athlete_age <= 24:
                athlete_age_group = "18_24"
            elif athlete_age <= 34:
                athlete_age_group = "25_34"
            elif athlete_age <= 44:
                athlete_age_group = "35_44"
            else:
                athlete_age_group = "45_plus"
            
            if athlete_age_group == target_age_group:
                score += 100 * 0.3
            elif abs(self._age_group_distance(athlete_age_group, target_age_group)) == 1:
                score += 70 * 0.3
            else:
                score += 30 * 0.3
            total_weight += 0.3
        
        # Gender matching
        if "gender" in target_demographics:
            target_gender = target_demographics["gender"].lower()
            athlete_gender = athlete_data.get("gender", "").lower()
            
            if target_gender == "any" or athlete_gender == target_gender:
                score += 100 * 0.2
            else:
                score += 40 * 0.2
            total_weight += 0.2
        
        # Interest alignment based on sport and bio
        if "interests" in target_demographics:
            target_interests = [interest.lower() for interest in target_demographics["interests"]]
            athlete_sport = athlete_data.get("sport", "").lower()
            athlete_bio = athlete_data.get("bio", "").lower()
            
            interest_matches = 0
            for interest in target_interests:
                if interest in athlete_sport or interest in athlete_bio:
                    interest_matches += 1
            
            if target_interests:
                interest_score = (interest_matches / len(target_interests)) * 100
                score += interest_score * 0.25
            else:
                score += 70 * 0.25
            total_weight += 0.25
        
        # Income/lifestyle matching based on follower count and engagement
        if "income_level" in target_demographics and athlete_metrics:
            target_income = target_demographics["income_level"].lower()
            total_followers = sum(m.get("followers", 0) for m in athlete_metrics)
            
            # Estimate influence level based on follower count
            if total_followers >= 1000000:
                influence_level = "high"
            elif total_followers >= 100000:
                influence_level = "medium"
            elif total_followers >= 10000:
                influence_level = "low_medium"
            else:
                influence_level = "low"
            
            income_mapping = {
                "low": ["low", "low_medium"],
                "medium": ["low_medium", "medium"],
                "high": ["medium", "high"]
            }
            
            if target_income in income_mapping and influence_level in income_mapping[target_income]:
                score += 90 * 0.25
            elif influence_level == "high":  # High influence generally appeals to all income levels
                score += 75 * 0.25
            else:
                score += 50 * 0.25
            total_weight += 0.25
        
        # Normalize score based on available data
        if total_weight > 0:
            final_score = score / total_weight
        else:
            final_score = 70  # Default score if no demographic data available
        
        return min(100, max(0, final_score))
    
    def _age_group_distance(self, age_group1: str, age_group2: str) -> int:
        """Calculate distance between age groups"""
        age_groups = ["under_18", "18_24", "25_34", "35_44", "45_plus"]
        try:
            idx1 = age_groups.index(age_group1)
            idx2 = age_groups.index(age_group2)
            return abs(idx1 - idx2)
        except ValueError:
            return 2  # Default distance for unknown age groups
    
    def _calculate_brand_safety_score(self, athlete_data: Dict, athlete_metrics: List[Dict]) -> float:
        """Calculate brand safety score based on content analysis"""
        score = 100  # Start with perfect score
        
        # Check for potential red flags in bio and content
        bio = athlete_data.get("bio", "").lower()
        
        # Red flag keywords that might indicate brand safety issues
        red_flag_keywords = [
            "controversial", "scandal", "arrest", "lawsuit", "drugs", "alcohol",
            "violence", "inappropriate", "suspended", "banned", "violation"
        ]
        
        moderate_risk_keywords = [
            "party", "wild", "crazy", "rebel", "outspoken", "political"
        ]
        
        # Check bio for red flags
        red_flags_found = sum(1 for keyword in red_flag_keywords if keyword in bio)
        moderate_risks_found = sum(1 for keyword in moderate_risk_keywords if keyword in bio)
        
        # Deduct points for red flags
        score -= red_flags_found * 25
        score -= moderate_risks_found * 10
        
        # Check social media engagement patterns (if available)
        if athlete_metrics:
            avg_engagement = np.mean([m.get("engagement_rate", 0) for m in athlete_metrics])
            total_followers = sum(m.get("followers", 0) for m in athlete_metrics)
            
            # Very high engagement with low followers might indicate fake engagement
            if avg_engagement > 15 and total_followers < 10000:
                score -= 15  # Potential fake engagement risk
            
            # Extremely low engagement might indicate inactive or problematic account
            if avg_engagement < 1 and total_followers > 50000:
                score -= 10  # Low engagement risk
        
        # Check for verification status (verified accounts are generally safer)
        if athlete_data.get("verified", False):
            score += 5
        
        # Check account age and completeness
        profile_completeness = 0
        required_fields = ["first_name", "last_name", "sport", "school", "bio"]
        completed_fields = sum(1 for field in required_fields if athlete_data.get(field))
        profile_completeness = (completed_fields / len(required_fields)) * 100
        
        if profile_completeness >= 80:
            score += 5
        elif profile_completeness < 50:
            score -= 10
        
        # Ensure score is within bounds
        return min(100, max(20, score))  # Minimum 20 to allow for rehabilitation
    
    def _estimate_athlete_rate(self, followers: int, engagement_score: int) -> float:
        """Estimate athlete's rate based on followers and engagement"""
        base_rate = followers * 0.01  # $0.01 per follower as baseline
        engagement_multiplier = 1 + (engagement_score / 100)
        return base_rate * engagement_multiplier
    
    async def find_athlete_matches(self, brand_data: Dict, athletes_data: List[Dict], preferences: Dict = None) -> List[Dict]:
        """Find and rank athlete matches for a brand using AI"""
        matches = []
        brand_profile = self._create_brand_profile_text(brand_data)
        brand_embedding = self.embedding_model.encode([brand_profile])[0]
        
        for athlete in athletes_data:
            try:
                # Get athlete metrics
                metrics_response = pb_client.client.collection("athlete_metrics").get_list(
                    filter=f"athlete = '{athlete['id']}'"
                )
                athlete_metrics = [m.to_dict() for m in metrics_response.items]
                
                # Create athlete profile and embedding
                athlete_profile = self._create_athlete_profile_text(athlete, athlete_metrics)
                athlete_embedding = self.embedding_model.encode([athlete_profile])[0]
                
                # Calculate semantic similarity
                similarity = cosine_similarity([brand_embedding], [athlete_embedding])[0][0]
                
                # Calculate detailed compatibility factors
                factors = self._calculate_compatibility_factors(athlete, brand_data, athlete_metrics)
                
                # Weighted overall score
                weights = {
                    "semantic_similarity": 0.3,
                    "sport_alignment": 0.25,
                    "engagement_quality": 0.2,
                    "budget_fit": 0.15,
                    "location_proximity": 0.05,
                    "audience_demographics": 0.03,
                    "brand_safety": 0.02
                }
                
                overall_score = (
                    similarity * 100 * weights["semantic_similarity"] +
                    factors["sport_alignment"] * weights["sport_alignment"] +
                    factors["engagement_quality"] * weights["engagement_quality"] +
                    factors["budget_fit"] * weights["budget_fit"] +
                    factors["location_proximity"] * weights["location_proximity"] +
                    factors["audience_demographics"] * weights["audience_demographics"] +
                    factors["brand_safety"] * weights["brand_safety"]
                )
                
                # Only include matches above threshold
                if overall_score >= (self.match_threshold * 100):
                    total_followers = sum(m.get("followers", 0) for m in athlete_metrics)
                    estimated_rate = self._estimate_athlete_rate(total_followers, factors["engagement_quality"])
                    
                    matches.append({
                        "athlete_id": athlete["id"],
                        "athlete_name": f"{athlete.get('first_name', '')} {athlete.get('last_name', '')}",
                        "sport": athlete.get("sport", ""),
                        "school": athlete.get("school", ""),
                        "overall_score": round(overall_score, 1),
                        "factors": factors,
                        "estimated_rate": round(estimated_rate, 2),
                        "total_followers": total_followers,
                        "profile_data": athlete
                    })
                    
            except Exception as e:
                logger.error(f"Error processing athlete {athlete.get('id')}", error=str(e))
                continue
        
        # Sort by overall score
        matches.sort(key=lambda x: x["overall_score"], reverse=True)
        return matches
    
    async def find_brand_matches(self, athlete_data: Dict, athlete_metrics: List[Dict], brands_data: List[Dict], preferences: Dict = None) -> List[Dict]:
        """Find and rank brand matches for an athlete using AI"""
        matches = []
        athlete_profile = self._create_athlete_profile_text(athlete_data, athlete_metrics)
        athlete_embedding = self.embedding_model.encode([athlete_profile])[0]
        
        for brand in brands_data:
            try:
                # Create brand profile and embedding
                brand_profile = self._create_brand_profile_text(brand)
                brand_embedding = self.embedding_model.encode([brand_profile])[0]
                
                # Calculate semantic similarity
                similarity = cosine_similarity([athlete_embedding], [brand_embedding])[0][0]
                
                # Calculate detailed compatibility factors
                factors = self._calculate_compatibility_factors(athlete_data, brand, athlete_metrics)
                
                # Weighted overall score (same weights as athlete matching)
                weights = {
                    "semantic_similarity": 0.3,
                    "sport_alignment": 0.25,
                    "engagement_quality": 0.2,
                    "budget_fit": 0.15,
                    "location_proximity": 0.05,
                    "audience_demographics": 0.03,
                    "brand_safety": 0.02
                }
                
                overall_score = (
                    similarity * 100 * weights["semantic_similarity"] +
                    factors["sport_alignment"] * weights["sport_alignment"] +
                    factors["engagement_quality"] * weights["engagement_quality"] +
                    factors["budget_fit"] * weights["budget_fit"] +
                    factors["location_proximity"] * weights["location_proximity"] +
                    factors["audience_demographics"] * weights["audience_demographics"] +
                    factors["brand_safety"] * weights["brand_safety"]
                )
                
                # Only include matches above threshold
                if overall_score >= (self.match_threshold * 100):
                    matches.append({
                        "brand_id": brand["id"],
                        "company_name": brand.get("company_name", ""),
                        "industry": brand.get("industry", ""),
                        "budget_range": f"${brand.get('budget_min', 0):,.0f} - ${brand.get('budget_max', 0):,.0f}",
                        "overall_score": round(overall_score, 1),
                        "factors": factors,
                        "profile_data": brand
                    })
                    
            except Exception as e:
                logger.error(f"Error processing brand {brand.get('id')}", error=str(e))
                continue
        
        # Sort by overall score
        matches.sort(key=lambda x: x["overall_score"], reverse=True)
        return matches
    
    async def calculate_detailed_compatibility(self, athlete_data: Dict, athlete_metrics: List[Dict], brand_data: Dict) -> Dict:
        """Calculate detailed compatibility analysis"""
        factors = self._calculate_compatibility_factors(athlete_data, brand_data, athlete_metrics)
        
        # Create embeddings for semantic analysis
        athlete_profile = self._create_athlete_profile_text(athlete_data, athlete_metrics)
        brand_profile = self._create_brand_profile_text(brand_data)
        
        athlete_embedding = self.embedding_model.encode([athlete_profile])[0]
        brand_embedding = self.embedding_model.encode([brand_profile])[0]
        
        semantic_similarity = cosine_similarity([athlete_embedding], [brand_embedding])[0][0]
        
        # Calculate weighted overall score
        weights = {
            "semantic_similarity": 0.3,
            "sport_alignment": 0.25,
            "engagement_quality": 0.2,
            "budget_fit": 0.15,
            "location_proximity": 0.05,
            "audience_demographics": 0.03,
            "brand_safety": 0.02
        }
        
        overall_score = (
            semantic_similarity * 100 * weights["semantic_similarity"] +
            sum(factors[key] * weights[key] for key in factors.keys() if key in weights)
        )
        
        return {
            "overall_score": round(overall_score, 1),
            "semantic_similarity": round(semantic_similarity * 100, 1),
            "compatibility_factors": factors,
            "recommendation": self._generate_recommendation(overall_score, factors),
            "estimated_success_rate": min(95, max(10, overall_score - 10))
        }
    
    def _generate_recommendation(self, overall_score: float, factors: Dict) -> str:
        """Generate human-readable recommendation based on compatibility"""
        if overall_score >= 85:
            return "Excellent match! High compatibility across all factors."
        elif overall_score >= 70:
            return "Good match with strong alignment in key areas."
        elif overall_score >= 55:
            return "Moderate match. Consider negotiating terms to improve fit."
        else:
            return "Low compatibility. May require significant adjustments."
    
    async def run_bulk_matching_analysis(self):
        """Run AI matching analysis for all active campaigns"""
        try:
            # Get all active campaigns
            campaigns = pb_client.client.collection("campaigns").get_list(
                filter="status = 'active'",
                per_page=100
            )
            
            for campaign in campaigns.items:
                await self._process_campaign_matches(campaign.to_dict())
                
        except Exception as e:
            logger.error("Bulk matching analysis failed", error=str(e))
            raise
    
    async def _process_campaign_matches(self, campaign: Dict):
        """Process AI matches for a specific campaign"""
        try:
            campaign_id = campaign["id"]
            logger.info("Processing campaign matches", campaign_id=campaign_id)
            
            # Get campaign with expanded brand data
            campaign_record = pb_client.client.collection("campaigns").get_one(
                campaign_id, expand="brand"
            )
            
            if not hasattr(campaign_record, 'expand') or not campaign_record.expand.get('brand'):
                logger.error("Campaign brand data not found", campaign_id=campaign_id)
                return
            
            brand_data = campaign_record.expand['brand'].__dict__
            
            # Get all eligible athletes based on campaign criteria
            filter_parts = ["status = 'active'"]
            
            # Filter by sport if specified in campaign
            if hasattr(campaign_record, 'target_sports') and campaign_record.target_sports:
                sports_filter = " || ".join([f"sport = '{sport}'" for sport in campaign_record.target_sports])
                filter_parts.append(f"({sports_filter})")
            
            # Filter by location if specified
            if hasattr(campaign_record, 'target_locations') and campaign_record.target_locations:
                location_filter = " || ".join([f"location ~ '{loc}'" for loc in campaign_record.target_locations])
                filter_parts.append(f"({location_filter})")
            
            # Filter by minimum followers if specified
            if hasattr(campaign_record, 'min_followers') and campaign_record.min_followers:
                # This would need to be implemented with a join on athlete_metrics
                pass
            
            athletes_filter = " && ".join(filter_parts)
            
            athletes_response = pb_client.client.collection("athletes").get_list(
                filter=athletes_filter,
                per_page=500,
                expand="user"
            )
            
            if not athletes_response.items:
                logger.info("No eligible athletes found", campaign_id=campaign_id)
                return
            
            # Convert to list of dicts for AI matching
            athletes_data = [athlete.__dict__ for athlete in athletes_response.items]
            
            # Run AI matching
            matches = await self.find_athlete_matches(brand_data, athletes_data)
            
            # Store matches in database
            stored_count = 0
            for match in matches[:50]:  # Limit to top 50 matches
                try:
                    match_data = {
                        "campaign": campaign_id,
                        "athlete": match["athlete_id"],
                        "brand": brand_data["id"],
                        "overall_score": match["overall_score"],
                        "factors": match["factors"],
                        "estimated_rate": match.get("estimated_rate", 0),
                        "total_followers": match.get("total_followers", 0),
                        "status": "pending",
                        "ai_recommendation": match.get("recommendation", ""),
                        "created": datetime.now().isoformat(),
                        "updated": datetime.now().isoformat()
                    }
                    
                    # Check if match already exists
                    existing_matches = pb_client.client.collection("matches").get_list(
                        filter=f"campaign = '{campaign_id}' && athlete = '{match['athlete_id']}'",
                        per_page=1
                    )
                    
                    if existing_matches.total_items > 0:
                        # Update existing match
                        match_data["updated"] = datetime.now().isoformat()
                        pb_client.client.collection("matches").update(
                            existing_matches.items[0].id, match_data
                        )
                    else:
                        # Create new match
                        pb_client.client.collection("matches").create(match_data)
                    
                    stored_count += 1
                    
                except Exception as e:
                    logger.error("Failed to store match", 
                               campaign_id=campaign_id, 
                               athlete_id=match["athlete_id"], 
                               error=str(e))
            
            # Update campaign with processing status
            pb_client.client.collection("campaigns").update(campaign_id, {
                "last_match_processing": datetime.now().isoformat(),
                "total_matches": stored_count
            })
            
            # Send notification to brand if matches were found
            if stored_count > 0 and hasattr(brand_data, 'user') and brand_data['user']:
                from app.worker.tasks import send_notification
                send_notification.delay(
                    brand_data['user'],
                    "new_matches_available",
                    {
                        "campaign_id": campaign_id,
                        "campaign_name": getattr(campaign_record, 'name', 'Your Campaign'),
                        "matches_count": stored_count,
                        "top_score": matches[0]["overall_score"] if matches else 0
                    }
                )
            
            logger.info("Campaign matches processed successfully", 
                       campaign_id=campaign_id, 
                       athletes_processed=len(athletes_data),
                       matches_found=len(matches),
                       matches_stored=stored_count)
                       
        except Exception as e:
            logger.error("Failed to process campaign matches", 
                        campaign_id=campaign.get("id", "unknown"), 
                        error=str(e))
            raise
    
    async def get_trending_athletes(self, sport: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get trending athletes based on recent engagement growth"""
        try:
            # Get athletes with recent metrics updates
            filter_parts = ["last_updated >= @now - '7d'"]
            if sport:
                filter_parts.append(f"athlete.sport = '{sport}'")
            
            filter_string = " && ".join(filter_parts)
            
            recent_metrics = pb_client.client.collection("athlete_metrics").get_list(
                filter=filter_string,
                expand="athlete",
                sort="-engagement_rate",
                per_page=limit * 2  # Get more to filter
            )
            
            trending = []
            for metric in recent_metrics.items:
                athlete = metric.expand.get("athlete")
                if athlete and len(trending) < limit:
                    trending.append({
                        "athlete_id": athlete.id,
                        "name": f"{athlete.first_name} {athlete.last_name}",
                        "sport": athlete.sport,
                        "followers": metric.followers,
                        "engagement_rate": metric.engagement_rate,
                        "trend_score": metric.engagement_rate * (metric.followers / 1000)
                    })
            
            return trending
            
        except Exception as e:
            logger.error("Error getting trending athletes", error=str(e))
            return []