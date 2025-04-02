import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.core.elasticsearch_client import ElasticsearchClient
from app.models.event import DicomEvent, AlertEvent
from app.config.dicom_config import DICOM_CONFIG
from app.utils.logging_utils import get_logger

logger = get_logger("alert_analyzer")

class AlertAnalyzer:
    
    def __init__(self, elasticsearch_client: ElasticsearchClient):
        """Initialize the alert analyzer."""
        self.es_client = elasticsearch_client
        self.alert_thresholds = DICOM_CONFIG.get('alert_thresholds', {})
        self.running = False
        self.thread = None
    
    def start(self, interval: int = 60):
    
        if self.running:
            logger.warning("Alert analyzer is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_analyzer, args=(interval,), daemon=True)
        self.thread.start()
        logger.info(f"Started alert analyzer with interval {interval} seconds")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            logger.info("Stopped alert analyzer")
    
    def _run_analyzer(self, interval: int):
        
        while self.running:
            try:
                self._analyze_events()
            except Exception as e:
                logger.error(f"Error in alert analyzer: {e}")
            
            time.sleep(interval)
    
    def _analyze_events(self):
        
        now = datetime.utcnow()
        
        self._analyze_connection_rate(now)
        
        self._analyze_operation_rate("C-FIND", now, self.alert_thresholds.get('c_find_rate', 20))
        
        self._analyze_operation_rate("C-MOVE", now, self.alert_thresholds.get('c_move_rate', 5))
        
        self._analyze_operation_rate("C-GET", now, self.alert_thresholds.get('c_get_rate', 5))
        
        self._analyze_honeytoken_access(now)
    
    def _analyze_connection_rate(self, now: datetime):
        
        threshold = self.alert_thresholds.get('connection_rate', 10)
        
        from_time = (now - timedelta(minutes=1)).isoformat()
        to_time = now.isoformat()
        
        query = {
            "bool": {
                "must": [
                    {"term": {"event_type": "ASSOCIATION_ESTABLISHED"}},
                    {"range": {"timestamp": {"gte": from_time, "lte": to_time}}}
                ]
            }
        }
        
        count = self.es_client.get_event_count(query)
        
        if count > threshold:
            alert = AlertEvent(
                timestamp=now.isoformat(),
                alert_type="HIGH_CONNECTION_RATE",
                severity="MEDIUM",
                client_ip=None,  
                message=f"High connection rate detected: {count} connections in the last minute",
                details={
                    "connection_count": count,
                    "threshold": threshold,
                    "time_period": "1 minute"
                },
                related_events=[]
            )
            
            logger.warning(f"Alert: {alert.message}")
            
            self.es_client.index_event({
                "event_type": "ALERT",
                **alert.dict()
            })
    
    def _analyze_operation_rate(self, operation: str, now: datetime, threshold: int):
       
        from_time = (now - timedelta(minutes=1)).isoformat()
        to_time = now.isoformat()
        
        query = {
            "bool": {
                "must": [
                    {"term": {"event_type": operation}},
                    {"range": {"timestamp": {"gte": from_time, "lte": to_time}}}
                ]
            }
        }
        
        count = self.es_client.get_event_count(query)
        
        if count > threshold:
            
            client_counts = self._get_client_operation_counts(operation, from_time, to_time)
            
            alert = AlertEvent(
                timestamp=now.isoformat(),
                alert_type=f"HIGH_{operation}_RATE",
                severity="MEDIUM",
                client_ip=None,  
                message=f"High {operation} rate detected: {count} operations in the last minute",
                details={
                    "operation_count": count,
                    "threshold": threshold,
                    "time_period": "1 minute",
                    "client_counts": client_counts
                },
                related_events=[]
            )
            
            
            logger.warning(f"Alert: {alert.message}")
            
            self.es_client.index_event({
                "event_type": "ALERT",
                **alert.dict()
            })
    
    def _get_client_operation_counts(self, operation: str, from_time: str, to_time: str) -> Dict[str, int]:
        
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"term": {"event_type": operation}},
                        {"range": {"timestamp": {"gte": from_time, "lte": to_time}}}
                    ]
                }
            },
            "aggs": {
                "clients": {
                    "terms": {
                        "field": "client_ip.keyword",
                        "size": 10
                    }
                }
            }
        }
        
        try:
            result = self.es_client.es.search(index=f"{self.es_client.index_prefix}*", body=query)
            client_counts = {
                bucket["key"]: bucket["doc_count"]
                for bucket in result["aggregations"]["clients"]["buckets"]
            }
            return client_counts
        except Exception as e:
            logger.error(f"Error getting client operation counts: {e}")
            return {}
    
    def _analyze_honeytoken_access(self, now: datetime):
        
        from_time = (now - timedelta(hours=1)).isoformat()
        to_time = now.isoformat()
        
        query = {
            "bool": {
                "must": [
                    {"bool": {
                        "should": [
                            {"wildcard": {"event_data.query_dataset": "*HONEYTOKEN*"}},
                            {"wildcard": {"event_data.dataset_summary": "*HONEYTOKEN*"}}
                        ]
                    }},
                    {"range": {"timestamp": {"gte": from_time, "lte": to_time}}}
                ]
            }
        }
        
        events = self.es_client.search_events(query)
        
        events_by_client = {}
        for event in events:
            client_ip = event.get("client_ip")
            if client_ip:
                if client_ip not in events_by_client:
                    events_by_client[client_ip] = []
                events_by_client[client_ip].append(event)
        
        for client_ip, client_events in events_by_client.items():
           
            alert = AlertEvent(
                timestamp=now.isoformat(),
                alert_type="HONEYTOKEN_ACCESS",
                severity="HIGH",
                client_ip=client_ip,
                message=f"Honeytoken data accessed by {client_ip}",
                details={
                    "access_count": len(client_events),
                    "first_access": client_events[0].get("timestamp"),
                    "last_access": client_events[-1].get("timestamp"),
                    "accessed_honeytokens": self._extract_honeytoken_ids(client_events)
                },
                related_events=[event.get("_id", "") for event in client_events]
            )
            
            logger.warning(f"Alert: {alert.message}")
            
            self.es_client.index_event({
                "event_type": "ALERT",
                **alert.dict()
            })
    
    def _extract_honeytoken_ids(self, events: List[Dict[str, Any]]) -> List[str]:
        
        honeytoken_ids = set()
        
        for event in events:
            event_data = event.get("event_data", {})
            
            query_dataset = event_data.get("query_dataset", "")
            if isinstance(query_dataset, str):
                for line in query_dataset.split("\n"):
                    if "HONEYTOKEN" in line:
                        parts = line.split("HONEYTOKEN-")
                        if len(parts) > 1:
                            honeytoken_id = parts[1].split()[0].strip()
                            honeytoken_ids.add(f"HONEYTOKEN-{honeytoken_id}")
            
            dataset_summary = event_data.get("dataset_summary", "")
            if isinstance(dataset_summary, str):
                for line in dataset_summary.split("\n"):
                    if "HONEYTOKEN" in line:
                        parts = line.split("HONEYTOKEN-")
                        if len(parts) > 1:
                            honeytoken_id = parts[1].split()[0].strip()
                            honeytoken_ids.add(f"HONEYTOKEN-{honeytoken_id}")
        
        return list(honeytoken_ids)
