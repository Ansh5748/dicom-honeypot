from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/status")
async def get_config_status():

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
