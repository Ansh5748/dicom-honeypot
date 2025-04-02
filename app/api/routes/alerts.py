from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.elasticsearch_client import ElasticsearchClient
from app.models.event import AlertEvent
from app.utils.logging_utils import get_logger

logger = get_logger("api.alerts")

router = APIRouter()

es_client = ElasticsearchClient()

@router.get("/", response_model=List[AlertEvent])
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, description="Maximum number of alerts to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    query = {"bool": {"must": []}}
    
    if severity:
        query["bool"]["must"].append({"term": {"severity": severity}})
    
    date_range = {}
    if from_date:
        date_range["gte"] = from_date
    
    if to_date:
        date_range["lte"] = to_date
    
    if date_range:
        query["bool"]["must"].append({"range": {"timestamp": date_range}})
    
    if not query["bool"]["must"]:
        query = {"match_all": {}}
    
    try:
        result = es_client.es.search(
            index=f"{es_client.index_prefix}alerts*",
            body={
                "query": query,
                "sort": [{"timestamp": {"order": "desc"}}],
                "size": limit,
                "from": offset
            }
        )
        
        alerts = [hit["_source"] for hit in result["hits"]["hits"]]
        return alerts
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")

@router.get("/count")
async def get_alert_count(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)")
):
    query = {"bool": {"must": []}}
    
    if severity:
        query["bool"]["must"].append({"term": {"severity": severity}})
    
    date_range = {}
    if from_date:
        date_range["gte"] = from_date
    
    if to_date:
        date_range["lte"] = to_date
    
    if date_range:
        query["bool"]["must"].append({"range": {"timestamp": date_range}})
    
    if not query["bool"]["must"]:
        query = {"match_all": {}}
    
    try:
        result = es_client.es.count(
            index=f"{es_client.index_prefix}alerts*",
            body={"query": query}
        )
        return {"count": result["count"]}
    except Exception as e:
        logger.error(f"Failed to get alert count: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert count")

@router.get("/severities")
async def get_alert_severities():
    try:
        query = {
            "size": 0,
            "aggs": {
                "severities": {
                    "terms": {
                        "field": "severity.keyword",
                        "size": 10
                    }
                }
            }
        }
        
        result = es_client.es.search(
            index=f"{es_client.index_prefix}alerts*",
            body=query
        )
        
        severities = [bucket["key"] for bucket in result["aggregations"]["severities"]["buckets"]]
        return {"severities": severities}
    except Exception as e:
        logger.error(f"Failed to get alert severities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert severities")
