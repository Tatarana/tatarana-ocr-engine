from fastapi import APIRouter
from datetime import datetime
import logging

from app.models.responses import HealthResponse, ConfigResponse
from app.config import APP_NAME, APP_VERSION, LLM_MODEL, LLM_BASE_URL, GOOGLE_DRIVE_FOLDER_ID

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=APP_VERSION,
        dependencies={
            "llm": "connected" if LLM_MODEL else "not_configured",
            "google_drive": "configured" if GOOGLE_DRIVE_FOLDER_ID else "not_configured"
        }
    )


@router.get("/show-config", response_model=ConfigResponse)
async def show_config():
    """Display current configuration (excluding secrets)."""
    app_config = {
        "name": APP_NAME,
        "version": APP_VERSION,
        "debug": False  # From config
    }
    
    llm_config = {
        "model": LLM_MODEL,
        "base_url": LLM_BASE_URL if LLM_BASE_URL else "default",
        "api_key": "***configured***" if LLM_MODEL else "***not_configured***"
    }
    
    google_drive_config = {
        "output_folder_id": GOOGLE_DRIVE_FOLDER_ID if GOOGLE_DRIVE_FOLDER_ID else "***not_configured***",
        "credentials": "***configured***" if GOOGLE_DRIVE_FOLDER_ID else "***not_configured***"
    }
    
    return ConfigResponse(
        app_config=app_config,
        llm_config=llm_config,
        google_drive_config=google_drive_config
    )
