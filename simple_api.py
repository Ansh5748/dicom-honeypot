from fastapi import FastAPI, HTTPException, Query, Path, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import os
import uvicorn
from datetime import datetime, timedelta

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/index.html")
def serve_index():
    return FileResponse("app/static/index.html")

@app.get("/events.html")
def serve_events():
    return FileResponse("app/static/events.html")

@app.get("/config.html")
def serve_config():
    return FileResponse("app/static/config.html")

@app.get("/about.html")
def serve_about():
    return FileResponse("app/static/about.html")

@app.get("/analytics.html")
def serve_analytics():
    return FileResponse("app/static/analytics.html")

@app.get("/architecture.png")
def serve_architecture():
    if os.path.exists("app/static/architecture.png"):
        return FileResponse("app/static/architecture.png")
    else:
        return JSONResponse(
            content={
                "message": "Architecture Diagram",
                "components": [
                    "DICOM Honeypot Server",
                    "Elasticsearch",
                    "Kibana",
                    "API Server",
                    "Logstash"
                ],
                "description": "This is a text representation of the DICOM Honeypot architecture."
            }
        )

@app.get("/api/events/")
def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    client_ip: Optional[str] = Query(None, description="Filter by client IP"),
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, description="Maximum number of events to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    events = [
        {
            "timestamp": "2025-04-01T10:15:30.123Z",
            "event_type": "C-ECHO",
            "client_ip": "192.168.1.100",
            "client_ae_title": "CLIENT_AE",
            "called_ae_title": "HONEYPOT",
            "event_data": {
                "message": "C-ECHO request received"
            }
        },
        {
            "timestamp": "2025-04-01T10:20:45.456Z",
            "event_type": "C-FIND",
            "client_ip": "192.168.1.101",
            "client_ae_title": "ATTACKER",
            "called_ae_title": "HONEYPOT",
            "event_data": {
                "message": "C-FIND request received",
                "query_dataset": "Dataset with 3 elements"
            }
        }
    ]
    return events[:limit]

@app.get("/api/events/count")
def get_event_count(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    client_ip: Optional[str] = Query(None, description="Filter by client IP"),
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)")
):
    return {"count": 42}  # Mock count

@app.get("/api/events/types")
def get_event_types():
    return {"event_types": ["C-ECHO", "C-FIND", "C-MOVE", "C-STORE", "ASSOCIATION_ESTABLISHED", "ASSOCIATION_RELEASED"]}

@app.get("/api/events/clients")
def get_client_ips():
    return {"client_ips": ["192.168.1.100", "192.168.1.101", "192.168.1.102"]}

@app.get("/api/stats/events")
def get_event_stats():
    return {
        "total_events": 156,
        "events_by_type": {
            "C-ECHO": 45,
            "C-FIND": 67,
            "C-MOVE": 23,
            "C-STORE": 21
        },
        "events_by_hour": {
            "00": 5, "01": 3, "02": 2, "03": 1, "04": 0, "05": 1,
            "06": 2, "07": 4, "08": 8, "09": 12, "10": 15, "11": 18,
            "12": 20, "13": 17, "14": 15, "15": 12, "16": 10, "17": 8,
            "18": 6, "19": 5, "20": 4, "21": 3, "22": 2, "23": 3
        },
        "top_operations": {
            "PatientRootQuery": 35,
            "StudyRootQuery": 25,
            "PatientStudyOnly": 15
        }
    }

@app.get("/api/stats/connections")
def get_connection_stats():
    return {
        "total_connections": 78,
        "active_connections": 3,
        "unique_ips": 12,
        "connection_rate": 2.5,
        "top_clients": {
            "192.168.1.100": 25,
            "192.168.1.101": 18,
            "192.168.1.102": 12
        }
    }

@app.get("/api/stats/")
def get_stats(from_date: str = None, to_date: str = None):
    return {
        "event_stats": {
            "total": 156,
            "by_type": {
                "C-ECHO": 45,
                "C-FIND": 67,
                "C-MOVE": 23,
                "C-STORE": 21
            }
        },
        "connection_stats": {
            "total": 78,
            "unique_ips": 12
        },
        "time_range": {
            "from": from_date,
            "to": to_date
        }
    }

@app.get("/api/alerts/")
def get_alerts():
    return [
        {
            "timestamp": "2025-04-01T10:15:30.123Z",
            "alert_type": "HONEYTOKEN_ACCESS",
            "severity": "HIGH",
            "client_ip": "192.168.1.100",
            "message": "Honeytoken data was accessed",
            "details": {
                "honeytoken_id": "HT-10001",
                "accessed_elements": ["PatientName", "PatientID"]
            }
        },
        {
            "timestamp": "2025-04-01T09:45:12.456Z",
            "alert_type": "MASS_DATA_RETRIEVAL",
            "severity": "MEDIUM",
            "client_ip": "192.168.1.101",
            "message": "Unusual number of C-FIND requests",
            "details": {
                "request_count": 150,
                "time_period_minutes": 5
            }
        }
    ]

@app.get("/api/config/status")
def get_config_status():
    return {
        "dicom_server": {
            "port": 11112,
            "ae_title": "HONEYPOT",
            "status": "running"
        },
        "elasticsearch": {
            "host": "elasticsearch",
            "port": 9200,
            "status": "connected"
        },
        "logging": {
            "level": "INFO",
            "file": "/app/logs/honeypot.log"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)