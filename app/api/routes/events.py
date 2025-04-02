from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.elasticsearch_client import ElasticsearchClient
from app.models.event import DicomEvent
from app.utils.logging_utils import get_logger

logger = get_logger("api.events")

router = APIRouter()

es_client = ElasticsearchClient()

@router.get("/", response_model=List[DicomEvent])
async def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    client_ip: Optional[str] = Query(None, description="Filter by client IP"),
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, description="Maximum number of events to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    query = {"bool": {"must": []}}
    
    if event_type:
        query["bool"]["must"].append({"term": {"event_type": event_type}})
    
    if client_ip:
        query["bool"]["must"].append({"term": {"client_ip.keyword": client_ip}})
    
    date_range = {}
    if from_date:
        date_range["gte"] = from_date
    
    if to_date:
        date_range["lte"] = to_date
    
    if date_range:
        query["bool"]["must"].append({"range": {"timestamp": date_range}})
    
    if not query["bool"]["must"]:
        query = {"match_all": {}}
    
    events = es_client.search_events(query, size=limit, from_=offset)
    
    return events

@router.get("/count")
async def get_event_count(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    client_ip: Optional[str] = Query(None, description="Filter by client IP"),
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)")
):
    query = {"bool": {"must": []}}
    
    if event_type:
        query["bool"]["must"].append({"term": {"event_type": event_type}})
    
    if client_ip:
        query["bool"]["must"].append({"term": {"client_ip.keyword": client_ip}})
    
    date_range = {}
    if from_date:
        date_range["gte"] = from_date
    
    if to_date:
        date_range["lte"] = to_date
    
    if date_range:
        query["bool"]["must"].append({"range": {"timestamp": date_range}})
    
    if not query["bool"]["must"]:
        query = {"match_all": {}}
    
    count = es_client.get_event_count(query)
    
    return {"count": count}

@router.get("/types")
async def get_event_types():
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
    
    try:
        result = es_client.es.search(index=f"{es_client.index_prefix}*", body=query)
        event_types = [bucket["key"] for bucket in result["aggregations"]["event_types"]["buckets"]]
        return {"event_types": event_types}
    except Exception as e:
        logger.error(f"Failed to get event types: {e}")
        raise HTTPException(status_code=500, detail="Failed to get event types")

@router.get("/clients")
async def get_client_ips():
    client_ips = es_client.get_unique_ips()
    return {"client_ips": client_ips}
