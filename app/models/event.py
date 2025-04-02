from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class DicomEvent(BaseModel):
    
    timestamp: str = Field(..., description="ISO-formatted timestamp of the event")
    event_type: str = Field(..., description="Type of DICOM event")
    client_ip: Optional[str] = Field(None, description="IP address of the client")
    client_ae_title: Optional[str] = Field(None, description="AE title of the client")
    called_ae_title: Optional[str] = Field(None, description="AE title that was called")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Additional event data")
    
    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2023-04-01T12:34:56.789Z",
                "event_type": "C-FIND",
                "client_ip": "192.168.1.100",
                "client_ae_title": "ATTACKER",
                "called_ae_title": "HONEYPOT",
                "event_data": {
                    "message": "C-FIND request received",
                    "query_dataset": "Dataset with 3 elements"
                }
            }
        }


class AlertEvent(BaseModel):
    
    timestamp: str = Field(..., description="ISO-formatted timestamp of the alert")
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Severity of the alert")
    client_ip: Optional[str] = Field(None, description="IP address of the client")
    message: str = Field(..., description="Alert message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional alert details")
    related_events: List[str] = Field(default_factory=list, description="IDs of related events")
    
    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2023-04-01T12:34:56.789Z",
                "alert_type": "HONEYTOKEN_ACCESS",
                "severity": "HIGH",
                "client_ip": "192.168.1.100",
                "message": "Honeytoken data was accessed",
                "details": {
                    "honeytoken_id": "HT-10001",
                    "accessed_elements": ["PatientName", "PatientID"]
                },
                "related_events": ["evt_123456789"]
            }
        }


class ConnectionStats(BaseModel):
    
    total_connections: int = Field(0, description="Total number of connections")
    active_connections: int = Field(0, description="Number of active connections")
    unique_ips: int = Field(0, description="Number of unique IP addresses")
    connection_rate: float = Field(0.0, description="Connections per minute")
    top_clients: Dict[str, int] = Field(default_factory=dict, description="Top clients by connection count")
    
    class Config:
        schema_extra = {
            "example": {
                "total_connections": 1250,
                "active_connections": 3,
                "unique_ips": 45,
                "connection_rate": 2.5,
                "top_clients": {
                    "192.168.1.100": 350,
                    "192.168.1.101": 275,
                    "192.168.1.102": 125
                }
            }
        }


class EventStats(BaseModel):
    
    total_events: int = Field(0, description="Total number of events")
    events_by_type: Dict[str, int] = Field(default_factory=dict, description="Events grouped by type")
    events_by_hour: Dict[str, int] = Field(default_factory=dict, description="Events grouped by hour")
    top_operations: Dict[str, int] = Field(default_factory=dict, description="Top DICOM operations")
    
    class Config:
        schema_extra = {
            "example": {
                "total_events": 5432,
                "events_by_type": {
                    "C-ECHO": 1200,
                    "C-FIND": 2500,
                    "C-MOVE": 800,
                    "C-STORE": 932
                },
                "events_by_hour": {
                    "00": 120,
                    "01": 85,
                    "02": 65,
                    # ... other hours
                    "23": 145
                },
                "top_operations": {
                    "PatientRootQuery": 1500,
                    "StudyRootQuery": 1000,
                    "PatientStudyOnly": 500
                }
            }
        }