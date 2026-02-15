import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DEBUG, LOG_LEVEL
from app.routers import orchestrator, bank_statements, credit_cards, system, input_folder

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Tatarana OCR Engine...")
    yield
    logger.info("Shutting down Tatarana OCR Engine...")


# Create FastAPI application
app = FastAPI(
    title="Tatarana OCR Engine",
    description="Microservice for processing bank and credit card statements using LLM-based OCR",
    version="1.0.0",
    lifespan=lifespan,
    debug=DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(orchestrator.router, prefix="/api/v1", tags=["orchestrator"])
app.include_router(bank_statements.router, prefix="/api/v1", tags=["bank-statements"])
app.include_router(credit_cards.router, prefix="/api/v1", tags=["credit-cards"])
app.include_router(system.router, prefix="/api/v1", tags=["system"])
app.include_router(input_folder.router, prefix="/api/v1", tags=["input-folder"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Tatarana OCR Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG
    )
