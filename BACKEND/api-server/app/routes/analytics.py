from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import structlog

from app.core.pocketbase import pb_client

logger = structlog.get_logger()
router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics(days: int = Query(30, ge=1, le=365)):
    """Get overall platform analytics for dashboard"""
    try:
        # Date range for filtering
        start_date = datetime.now() - timedelta(days=days)
        start_date_str = start_date.isoformat()
        
        # Get counts
        total_athletes = pb_client.client.collection("athletes").get_list(per_page=1).total_items
        total_brands = pb_client.client.collection("brands").get_list(per_page=1).total_items
        total_campaigns = pb_client.client.collection("campaigns").get_list(per_page=1).total_items
        
        # Get recent deals
        recent_deals = pb_client.client.collection("deals").get_list(
            filter=f"created >= '{start_date_str}'",
            per_page=500,
            expand="athlete,brand"
        )
        
        # Calculate metrics
        active_deals = len([d for d in recent_deals.items if d.status in ["active", "negotiating", "pending_signatures"]])
        completed_deals = len([d for d in recent_deals.items if d.status == "completed"])
        total_deal_value = sum(d.value for d in recent_deals.items if d.value)
        
        # Success rate
        success_rate = (completed_deals / len(recent_deals.items) * 100) if recent_deals.items else 0
        
        # Sport distribution
        sport_stats = {}
        for deal in recent_deals.items:
            if hasattr(deal, 'expand') and deal.expand.get('athlete'):
                sport = deal.expand['athlete'].sport
                sport_stats[sport] = sport_stats.get(sport, 0) + 1
        
        # Deal value trends (simplified)
        daily_values = {}
        for deal in recent_deals.items:
            day = deal.created[:10]  # YYYY-MM-DD
            daily_values[day] = daily_values.get(day, 0) + (deal.value or 0)
        
        analytics = {
            "overview": {
                "total_athletes": total_athletes,
                "total_brands": total_brands,
                "total_campaigns": total_campaigns,
                "period_deals": len(recent_deals.items),
                "active_deals": active_deals,
                "success_rate": round(success_rate, 2)
            },
            "financial": {
                "total_deal_value": total_deal_value,
                "avg_deal_value": total_deal_value / len(recent_deals.items) if recent_deals.items else 0,
                "daily_trends": daily_values
            },
            "sports_distribution": sport_stats,
            "period_days": days
        }
        
        logger.info("Dashboard analytics retrieved", period_days=days)
        return analytics
        
    except Exception as e:
        logger.error("Failed to get dashboard analytics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard analytics")

@router.get("/market-insights")
async def get_market_insights(sport: Optional[str] = Query(None)):
    """Get AI-generated market insights"""
    try:
        # Get market data
        if sport:
            # Sport-specific insights
            athletes = pb_client.client.collection("athletes").get_list(
                filter=f"sport = '{sport}'",
                per_page=500
            )
            
            deals = pb_client.client.collection("deals").get_list(
                filter=f"athlete.sport = '{sport}'",
                expand="athlete,brand",
                per_page=500
            )
        else:
            # Overall market insights
            athletes = pb_client.client.collection("athletes").get_list(per_page=500)
            deals = pb_client.client.collection("deals").get_list(
                expand="athlete,brand",
                per_page=500
            )
        
        # Calculate market metrics
        total_athletes = len(athletes.items)
        active_deals = len([d for d in deals.items if d.status in ["active", "negotiating"]])
        avg_deal_value = sum(d.value for d in deals.items if d.value) / len(deals.items) if deals.items else 0
        
        # Industry distribution
        industry_stats = {}
        for deal in deals.items:
            if hasattr(deal, 'expand') and deal.expand.get('brand'):
                industry = deal.expand['brand'].industry
                industry_stats[industry] = industry_stats.get(industry, 0) + 1
        
        # Market saturation calculation
        campaigns = pb_client.client.collection("campaigns").get_list(
            filter="status = 'active'",
            per_page=500
        )
        
        market_saturation = min(100, (len(campaigns.items) / max(1, total_athletes)) * 100)
        
        # Growth trend (simplified - would need historical data)
        growth_trend = "stable"
        if len(deals.items) > 0:
            recent_deals = [d for d in deals.items if 
                           datetime.fromisoformat(d.created) > datetime.now() - timedelta(days=30)]
            if len(recent_deals) > len(deals.items) * 0.3:
                growth_trend = "rising"
            elif len(recent_deals) < len(deals.items) * 0.1:
                growth_trend = "declining"
        
        insights = {
            "sport": sport or "overall",
            "metrics": {
                "total_athletes": total_athletes,
                "active_deals": active_deals,
                "average_deal_value": round(avg_deal_value, 2),
                "market_saturation": round(market_saturation, 1)
            },
            "trends": {
                "growth_trend": growth_trend,
                "top_industries": sorted(industry_stats.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            "ai_insights": [
                f"Average deal value in {sport or 'the platform'}: ${avg_deal_value:,.0f}",
                f"Market activity level: {'High' if active_deals > 20 else 'Moderate' if active_deals > 5 else 'Low'}",
                f"Competition level: {'High' if market_saturation > 70 else 'Moderate' if market_saturation > 30 else 'Low'}"
            ]
        }
        
        logger.info("Market insights retrieved", sport=sport)
        return insights
        
    except Exception as e:
        logger.error("Failed to get market insights", sport=sport, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve market insights")

@router.get("/trends/athletes")
async def get_athlete_trends(
    sport: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    metric: str = Query("engagement", regex="^(engagement|followers|deals)$")
):
    """Get trending athletes based on various metrics"""
    try:
        # Get athletes with recent metrics
        filter_parts = []
        if sport:
            filter_parts.append(f"athlete.sport = '{sport}'")
        
        filter_string = " && ".join(filter_parts) if filter_parts else ""
        
        metrics = pb_client.client.collection("athlete_metrics").get_list(
            filter=filter_string,
            expand="athlete",
            sort=f"-{metric}_rate" if metric == "engagement" else f"-{metric}",
            per_page=limit * 2
        )
        
        trending = []
        seen_athletes = set()
        
        for metric_record in metrics.items:
            if hasattr(metric_record, 'expand') and metric_record.expand.get('athlete'):
                athlete = metric_record.expand['athlete']
                if athlete.id not in seen_athletes:
                    seen_athletes.add(athlete.id)
                    
                    # Calculate trend score
                    if metric == "engagement":
                        trend_score = metric_record.engagement_rate or 0
                    elif metric == "followers":
                        trend_score = metric_record.followers or 0
                    else:  # deals
                        # Get deal count for athlete
                        athlete_deals = pb_client.client.collection("deals").get_list(
                            filter=f"athlete = '{athlete.id}' && status = 'active'"
                        )
                        trend_score = len(athlete_deals.items)
                    
                    trending.append({
                        "athlete_id": athlete.id,
                        "name": f"{athlete.first_name} {athlete.last_name}",
                        "sport": athlete.sport,
                        "school": athlete.school,
                        "trend_metric": metric,
                        "trend_score": trend_score,
                        "profile_image": athlete.profile_image
                    })
                    
                    if len(trending) >= limit:
                        break
        
        logger.info("Athlete trends retrieved", metric=metric, sport=sport, count=len(trending))
        return {
            "metric": metric,
            "sport": sport,
            "athletes": trending
        }
        
    except Exception as e:
        logger.error("Failed to get athlete trends", metric=metric, sport=sport, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve athlete trends")

@router.get("/performance/deals")
async def get_deal_performance_analytics(
    days: int = Query(30, ge=1, le=365),
    sport: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """Get deal performance analytics"""
    try:
        # Date filtering
        start_date = datetime.now() - timedelta(days=days)
        filter_parts = [f"created >= '{start_date.isoformat()}'"]
        
        if sport:
            filter_parts.append(f"athlete.sport = '{sport}'")
        if status:
            filter_parts.append(f"status = '{status}'")
        
        filter_string = " && ".join(filter_parts)
        
        deals = pb_client.client.collection("deals").get_list(
            filter=filter_string,
            expand="athlete,brand",
            per_page=500
        )
        
        # Performance calculations
        total_deals = len(deals.items)
        deal_values = [d.value for d in deals.items if d.value]
        
        performance = {
            "total_deals": total_deals,
            "total_value": sum(deal_values),
            "avg_deal_value": sum(deal_values) / len(deal_values) if deal_values else 0,
            "median_deal_value": sorted(deal_values)[len(deal_values)//2] if deal_values else 0,
            "status_distribution": {},
            "value_ranges": {
                "under_5k": len([v for v in deal_values if v < 5000]),
                "5k_to_15k": len([v for v in deal_values if 5000 <= v < 15000]),
                "15k_to_50k": len([v for v in deal_values if 15000 <= v < 50000]),
                "over_50k": len([v for v in deal_values if v >= 50000])
            }
        }
        
        # Status distribution
        for deal in deals.items:
            status = deal.status
            performance["status_distribution"][status] = performance["status_distribution"].get(status, 0) + 1
        
        logger.info("Deal performance analytics retrieved", days=days, sport=sport)
        return performance
        
    except Exception as e:
        logger.error("Failed to get deal performance analytics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve deal performance analytics")