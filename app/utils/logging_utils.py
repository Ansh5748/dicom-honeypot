
import logging
import os
from datetime import datetime
from elasticsearch import Elasticsearch, exceptions

from app.utils.logging_utils import get_logger

class ElasticsearchClient:
    
    def __init__(self):
        self.logger = get_logger("elasticsearch_client")
        self.host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
        self.port = os.environ.get("ELASTICSEARCH_PORT", "9200")
        self.index_prefix = "dicom-honeypot-"
        
        self.es = self._connect()
        
        self._create_index()
    
    def _connect(self):
        try:
            es = Elasticsearch([f"http://{self.host}:{self.port}"])
            self.logger.info(f"Connected to Elasticsearch at {self.host}:{self.port}")
            return es
        except Exception as e:
            self.logger.error(f"Failed to connect to Elasticsearch: {e}")
            return DummyElasticsearchClient()
    
    def _create_index(self):
        try:
            index_name = f"{self.index_prefix}{datetime.now().strftime('%Y-%m')}"
            
            if not self.es.indices.exists(index=index_name):
                self.es.indices.create(
                    index=index_name,
                    body={
                        "mappings": {
                            "properties": {
                                "timestamp": {"type": "date"},
                                "event_type": {"type": "keyword"},
                                "client_ip": {"type": "ip"},
                                "client_ae_title": {"type": "keyword"},
                                "called_ae_title": {"type": "keyword"},
                                "event_data": {"type": "object"}
                            }
                        }
                    }
                )
                self.logger.info(f"Created index {index_name}")
        except Exception as e:
            self.logger.error(f"Failed to create index: {e}")
    
    def index_event(self, event):
        
        try:
            index_name = f"{self.index_prefix}{datetime.now().strftime('%Y-%m')}"
            
            self.es.index(index=index_name, body=event)
        except Exception as e:
            self.logger.error(f"Failed to index event: {e}")
    
    def search_events(self, query, size=100, from_=0):
        
        try:
            result = self.es.search(
                index=f"{self.index_prefix}*",
                body={
                    "query": query,
                    "sort": [{"timestamp": {"order": "desc"}}],
                    "from": from_,
                    "size": size
                }
            )
            
            events = [hit["_source"] for hit in result["hits"]["hits"]]
            return events
        except Exception as e:
            self.logger.error(f"Failed to search events: {e}")
            return []
    
    def get_event_count(self, query):
        try:
            result = self.es.count(
                index=f"{self.index_prefix}*",
                body={"query": query}
            )
            
            return result["count"]
        except Exception as e:
            self.logger.error(f"Failed to get event count: {e}")
            return 0
    
    def get_unique_ips(self):
        
        try:
            query = {
                "size": 0,
                "aggs": {
                    "unique_ips": {
                        "terms": {
                            "field": "client_ip.keyword",
                            "size": 1000
                        }
                    }
                }
            }
            
            result = self.es.search(index=f"{self.index_prefix}*", body=query)
            ips = [bucket["key"] for bucket in result["aggregations"]["unique_ips"]["buckets"]]
            return ips
        except Exception as e:
            self.logger.error(f"Failed to get unique IPs: {e}")
            return []


class DummyElasticsearchClient:
    
    def __init__(self):
        self.logger = get_logger("dummy_elasticsearch")
    
    def __getattr__(self, name):
        def dummy_method(*args, **kwargs):
            self.logger.warning(f"Elasticsearch not available, called: {name}")
            
            if name == "search":
                return {"hits": {"hits": []}}
            elif name == "count":
                return {"count": 0}
            elif name == "indices":
                return self
            else:
                return None
        
        return dummy_method
