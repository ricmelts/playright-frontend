import numpy as np
from typing import Dict, List, Any, Tuple
import structlog
from datetime import datetime

logger = structlog.get_logger()

class CompatibilityModel:
    """Model for calculating detailed compatibility factors between athletes and brands"""
    
    def __init__(self):
        # Sport compatibility matrix
        self.sport_compatibility = {
            "basketball": ["basketball", "sports_apparel", "fitness", "nutrition"],
            "soccer": ["soccer", "football", "sports_apparel", "fitness"],
            "tennis": ["tennis", "sports_apparel", "fitness", "luxury"],
            "swimming": ["swimming", "fitness", "nutrition", "sports_apparel"],
            "football": ["football", "sports_apparel", "fitness", "automotive"],
            "baseball": ["baseball", "sports_apparel", "food_beverage"],
            "golf": ["golf", "luxury", "financial", "automotive"],
            "track": ["track", "sports_apparel", "fitness", "nutrition"]
        }
        
        # Industry-sport affinity scores
        self.industry_sport_affinity = {
            "sports_apparel": {"basketball": 100, "soccer": 95, "tennis": 90, "swimming": 85, "football": 100},
            "fitness": {"basketball": 85, "soccer": 80, "tennis": 90, "swimming": 100, "track": 95},
            "nutrition": {"basketball": 70, "soccer": 75, "swimming": 90, "track": 85, "football": 80},
            "automotive": {"football": 85, "basketball": 70, "golf": 80, "baseball": 60},
            "technology": {"basketball": 75, "soccer": 70, "tennis": 65, "swimming": 60}
        }
    
    def calculate_compatibility_factors(self, athlete_data: Dict, brand_data: Dict, athlete_metrics: List[Dict]) -> Dict[str, float]:
        """Calculate all compatibility factors"""
        factors = {}
        
        # Sport alignment
        factors["sport_alignment"] = self._calculate_sport_alignment(athlete_data, brand_data)
        
        # Audience demographics match
        factors["audience_match"] = self._calculate_audience_match(athlete_metrics, brand_data)
        
        # Engagement quality
        factors["engagement_quality"] = self._calculate_engagement_quality(athlete_metrics)
        
        # Budget compatibility
        factors["budget_compatibility"] = self._calculate_budget_compatibility(athlete_metrics, brand_data)
        
        # Location proximity
        factors["location_proximity"] = self._calculate_location_proximity(athlete_data, brand_data)
        
        # Brand safety score
        factors["brand_safety"] = self._calculate_brand_safety(athlete_data, athlete_metrics)
        
        return factors
    
    def _calculate_sport_alignment(self, athlete_data: Dict, brand_data: Dict) -> float:
        """Calculate sport-brand alignment score"""
        athlete_sport = athlete_data.get("sport", "").lower()
        brand_industry = brand_data.get("industry", "").lower()
        preferred_sports = brand_data.get("preferred_sports", [])
        
        # Direct sport match
        if athlete_sport in [s.lower() for s in preferred_sports]:
            return 100.0
        
        # Industry-sport affinity
        if brand_industry in self.industry_sport_affinity:
            sport_scores = self.industry_sport_affinity[brand_industry]
            return sport_scores.get(athlete_sport, 40.0)  # Default moderate score
        
        # Generic compatibility
        if athlete_sport in self.sport_compatibility:
            compatible_industries = self.sport_compatibility[athlete_sport]
            if brand_industry in compatible_industries:
                return 75.0
        
        return 30.0  # Low compatibility
    
    def _calculate_audience_match(self, athlete_metrics: List[Dict], brand_data: Dict) -> float:
        """Calculate audience demographics alignment"""
        if not athlete_metrics:
            return 50.0  # Default score when no metrics available
        
        brand_target = brand_data.get("target_demographics", {})
        if not brand_target:
            return 70.0  # Default when brand has no specific targeting
        
        match_scores = []
        
        for metric in athlete_metrics:
            audience_demo = metric.get("audience_demographics", {})
            if not audience_demo:
                continue
            
            # Age group alignment
            athlete_age_groups = audience_demo.get("age_groups", {})
            brand_age_groups = brand_target.get("age_groups", {})
            
            if athlete_age_groups and brand_age_groups:
                age_overlap = 0
                for age_group, athlete_pct in athlete_age_groups.items():
                    brand_pct = brand_age_groups.get(age_group, 0)
                    age_overlap += min(athlete_pct, brand_pct)
                match_scores.append(age_overlap)
            
            # Gender alignment
            athlete_gender = audience_demo.get("gender", {})
            brand_gender = brand_target.get("gender", {})
            
            if athlete_gender and brand_gender:
                gender_overlap = 0
                for gender, athlete_pct in athlete_gender.items():
                    brand_pct = brand_gender.get(gender, 0)
                    gender_overlap += min(athlete_pct, brand_pct)
                match_scores.append(gender_overlap)
        
        return np.mean(match_scores) if match_scores else 60.0
    
    def _calculate_engagement_quality(self, athlete_metrics: List[Dict]) -> float:
        """Calculate engagement quality score"""
        if not athlete_metrics:
            return 30.0
        
        engagement_rates = [m.get("engagement_rate", 0) for m in athlete_metrics]
        avg_engagement = np.mean(engagement_rates) if engagement_rates else 0
        
        # Score based on engagement rate benchmarks
        if avg_engagement >= 10:
            return 100.0
        elif avg_engagement >= 7:
            return 90.0
        elif avg_engagement >= 5:
            return 75.0
        elif avg_engagement >= 3:
            return 60.0
        elif avg_engagement >= 1:
            return 40.0
        else:
            return 20.0
    
    def _calculate_budget_compatibility(self, athlete_metrics: List[Dict], brand_data: Dict) -> float:
        """Calculate budget fit score"""
        if not athlete_metrics:
            return 50.0
        
        # Estimate athlete's market rate
        total_followers = sum(m.get("followers", 0) for m in athlete_metrics)
        avg_engagement = np.mean([m.get("engagement_rate", 0) for m in athlete_metrics])
        
        # Rate estimation formula (simplified)
        base_rate = total_followers * 0.005  # $0.005 per follower baseline
        engagement_multiplier = 1 + (avg_engagement / 100)
        estimated_rate = base_rate * engagement_multiplier
        
        # Brand budget
        brand_budget_min = brand_data.get("budget_min", 0)
        brand_budget_max = brand_data.get("budget_max", 0)
        
        if brand_budget_max == 0:
            return 60.0  # Default when no budget specified
        
        # Score based on fit within budget range
        if estimated_rate <= brand_budget_min:
            return 95.0  # Under-budget
        elif estimated_rate <= brand_budget_max:
            return 100.0  # Perfect fit
        elif estimated_rate <= brand_budget_max * 1.2:
            return 70.0   # Slightly over budget
        elif estimated_rate <= brand_budget_max * 1.5:
            return 40.0   # Significantly over budget
        else:
            return 15.0   # Way over budget
    
    def _calculate_location_proximity(self, athlete_data: Dict, brand_data: Dict) -> float:
        """Calculate geographic proximity score"""
        athlete_location = athlete_data.get("location", "").lower()
        brand_location = brand_data.get("location", "").lower()
        
        if not athlete_location or not brand_location:
            return 50.0
        
        # Exact match
        if athlete_location == brand_location:
            return 100.0
        
        # State/region match (simplified)
        athlete_parts = athlete_location.split(",")
        brand_parts = brand_location.split(",")
        
        # Check state match (assuming format "City, State")
        if len(athlete_parts) >= 2 and len(brand_parts) >= 2:
            athlete_state = athlete_parts[-1].strip()
            brand_state = brand_parts[-1].strip()
            if athlete_state == brand_state:
                return 80.0
        
        # Check for any common location elements
        if any(part.strip() in brand_location for part in athlete_parts):
            return 60.0
        
        return 30.0  # No geographic alignment
    
    def _calculate_brand_safety(self, athlete_data: Dict, athlete_metrics: List[Dict]) -> float:
        """Calculate brand safety score"""
        safety_score = 85.0  # Start with good baseline
        
        # Factors that could affect brand safety:
        # 1. Profile completeness
        required_fields = ["first_name", "last_name", "sport", "school", "bio"]
        completed_fields = sum(1 for field in required_fields if athlete_data.get(field))
        completeness_score = (completed_fields / len(required_fields)) * 100
        
        if completeness_score < 60:
            safety_score -= 15
        
        # 2. Social media presence consistency
        if athlete_metrics:
            platform_count = len(athlete_metrics)
            if platform_count >= 3:
                safety_score += 10  # Multi-platform presence is good
            elif platform_count == 1:
                safety_score -= 5   # Single platform is riskier
        
        # 3. NIL eligibility
        if not athlete_data.get("nil_eligible", True):
            safety_score -= 30  # Major risk factor
        
        return max(20.0, min(100.0, safety_score))
    
    def generate_recommendation(self, overall_score: float, factors: Dict[str, float]) -> str:
        """Generate human-readable recommendation"""
        if overall_score >= 85:
            return "Excellent match! Strong compatibility across all key factors. Highly recommended for partnership."
        elif overall_score >= 70:
            return "Good match with solid alignment. Recommended with standard negotiation approach."
        elif overall_score >= 55:
            # Identify weak areas
            weak_factors = [name for name, score in factors.items() if score < 50]
            if weak_factors:
                weak_list = ", ".join(weak_factors[:2])
                return f"Moderate match. Consider addressing {weak_list} before proceeding."
            else:
                return "Moderate match. Standard due diligence recommended."
        else:
            return "Low compatibility. Significant alignment issues detected. Consider alternative partnerships."
    
    def assess_risk_factors(self, athlete_data: Dict, brand_data: Dict, factors: Dict[str, float]) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Low engagement risk
        if factors.get("engagement_quality", 0) < 40:
            risks.append("Low social media engagement may limit campaign reach")
        
        # Budget mismatch risk
        if factors.get("budget_compatibility", 0) < 30:
            risks.append("Significant budget mismatch - athlete may be overpriced")
        
        # Sport misalignment risk
        if factors.get("sport_alignment", 0) < 50:
            risks.append("Poor sport-industry alignment may confuse target audience")
        
        # Geographic risk
        if factors.get("location_proximity", 0) < 40:
            risks.append("Geographic distance may complicate campaign logistics")
        
        # Brand safety risk
        if factors.get("brand_safety", 0) < 60:
            risks.append("Brand safety concerns detected - additional vetting recommended")
        
        # NIL eligibility risk
        if not athlete_data.get("nil_eligible", True):
            risks.append("NIL eligibility issues - legal review required")
        
        return risks
    
    def get_optimization_suggestions(self, factors: Dict[str, float]) -> List[str]:
        """Generate suggestions for improving compatibility"""
        suggestions = []
        
        # Low engagement suggestions
        if factors.get("engagement_quality", 0) < 60:
            suggestions.append("Focus on content strategy improvement to boost engagement rates")
        
        # Budget optimization
        if factors.get("budget_compatibility", 0) < 70:
            suggestions.append("Consider performance-based compensation to align with budget constraints")
        
        # Audience alignment
        if factors.get("audience_match", 0) < 60:
            suggestions.append("Develop targeted content that appeals to brand's core demographics")
        
        # Geographic considerations
        if factors.get("location_proximity", 0) < 50:
            suggestions.append("Plan virtual campaign elements to overcome geographic limitations")
        
        # Sport alignment improvement
        if factors.get("sport_alignment", 0) < 70:
            suggestions.append("Create crossover content that bridges sport and brand industry")
        
        return suggestions