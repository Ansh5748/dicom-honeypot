from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DICOM Honeypot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "DICOM Honeypot API is running"}

@app.get("/api/events/clients")
async def get_clients():
    return {"client_ips": []}

@app.get("/api/events/types")
async def get_event_types():
    return {"event_types": ["C-ECHO", "C-FIND", "C-MOVE", "C-STORE"]}

@app.get("/api/events/")
async def get_events():
    return []

@app.get("/api/config/status")
async def get_status():
    return {
        "dicom_server": {
            "port": 11112,
            "ae_title": "HONEYPOT"
        },
        "elasticsearch": {
            "host": "elasticsearch",
            "port": 9200,
            "status": "connected"
        },
        "logging": {
            "level": "INFO"
        }
    }
