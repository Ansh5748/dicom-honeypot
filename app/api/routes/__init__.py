from fastapi import APIRouter
from app.api.routes import events, config

router = APIRouter()

router.include_router(events.router, prefix="/events", tags=["events"])
router.include_router(config.router, prefix="/config", tags=["config"])
