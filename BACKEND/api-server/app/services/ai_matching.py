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
        
        # Default values for factors not yet implemented
        factors["audience_demographics"] = 75
        factors["brand_safety"] = 85
        
        return factors
    
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
        # This would typically update a matches table or cache
        # For now, we'll just log the process
        logger.info("Processing campaign matches", campaign_id=campaign["id"])
    
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