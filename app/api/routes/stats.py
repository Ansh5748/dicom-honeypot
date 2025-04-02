from fastapi import APIRouter, Query
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.elasticsearch_client import ElasticsearchClient
from app.utils.logging_utils import get_logger

logger = get_logger("api.stats")

router = APIRouter()

es_client = ElasticsearchClient()

@router.get("/connections")
async def get_connection_stats():
    return {
        "total_connections": 0,
        "active_connections": 0,
        "unique_ips": 0,
        "connection_rate": 0.0,
        "top_clients": {}
    }

@router.get("/events")
async def get_event_stats(
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)")
):
    date_range = {}
    if from_date:
        date_range["gte"] = from_date
    if to_date:
        date_range["lte"] = to_date
    
    events_by_type = {}
    try:
        query = {
            "size": 0,
            "aggs": {
                "event_types": {
                    "terms": {
                        "field": "event_type.keyword",
                        "size": 100
                    }
                }
            }
        }
        
        if date_range:
            query["query"] = {"range": {"timestamp": date_range}}
        
        result = es_client.es.search(index=f"{es_client.index_prefix}*", body=query)
        for bucket in result["aggregations"]["event_types"]["buckets"]:
            events_by_type[bucket["key"]] = bucket["doc_count"]
    except Exception as e:
        logger.error(f"Failed to get event types: {e}")
        events_by_type = {}
    
    events_by_hour = {}
    try:
        query = {
            "size": 0,
            "aggs": {
                "events_by_hour": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "hour",
                        "format": "HH"
                    }
                }
            }
        }
        
        if date_range:
            query["query"] = {"range": {"timestamp": date_range}}
        
        result = es_client.es.search(index=f"{es_client.index_prefix}*", body=query)
        for bucket in result["aggregations"]["events_by_hour"]["buckets"]:
            events_by_hour[bucket["key_as_string"]] = bucket["doc_count"]
    except Exception as e:
        logger.error(f"Failed to get events by hour: {e}")
        
        for hour in range(24):
            events_by_hour[f"{hour:02d}"] = 0
    
    events_by_day = {}
    try:
        query = {
            "size": 0,
            "aggs": {
                "events_by_day": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "day",
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        }
        
        if date_range:
            query["query"] = {"range": {"timestamp": date_range}}
        
        result = es_client.es.search(index=f"{es_client.index_prefix}*", body=query)
        for bucket in result["aggregations"]["events_by_day"]["buckets"]:
            events_by_day[bucket["key_as_string"]] = bucket["doc_count"]
    except Exception as e:
        logger.error(f"Failed to get events by day: {e}")
        events_by_day = {}
    
    total_events = sum(events_by_type.values())
    
    return {
        "total_events": total_events,
        "events_by_type": events_by_type,
        "events_by_hour": events_by_hour,
        "events_by_day": events_by_day,
        "top_operations": {}
    }

@router.get("/")
async def get_all_stats(
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)")
):
    connection_stats = await get_connection_stats()
    event_stats = await get_event_stats(from_date, to_date)
    
    alert_stats = {
        "total_alerts": 0,
        "alerts_by_type": {},
        "alerts_by_severity": {}
    }
    
    return {
        "connection_stats": connection_stats,
        "event_stats": event_stats,
        "alert_stats": alert_stats,
        "recent_alerts": []
    }
