from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class IdentifyFileResponse(BaseModel):
    """Response model for file identification."""
    bank: str = Field(..., description="Identified bank")
    document_type: str = Field(..., description="Document type: bank_statement or credit_card")
    confidence: float = Field(..., description="Confidence score (0-1)")
    file_id: str = Field(..., description="Original file ID")


class OCRResponse(BaseModel):
    """Response model for OCR processing."""
    success: bool = Field(..., description="Processing success status")
    message: str = Field(..., description="Status message")
    csv_file_id: Optional[str] = Field(None, description="Google Drive file ID for generated CSV")
    csv_file_url: Optional[str] = Field(None, description="Google Drive URL for generated CSV")
    transactions_count: Optional[int] = Field(None, description="Number of transactions extracted")
    processing_time_seconds: Optional[float] = Field(None, description="Processing time in seconds")
    error: Optional[str] = Field(None, description="Error message if processing failed")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="Application version")
    dependencies: Dict[str, str] = Field(..., description="Dependency status")


class ConfigResponse(BaseModel):
    """Response model for configuration display."""
    app_config: Dict[str, Any] = Field(..., description="Application configuration (excluding secrets)")
    llm_config: Dict[str, Any] = Field(..., description="LLM configuration (excluding secrets)")
    google_drive_config: Dict[str, Any] = Field(..., description="Google Drive configuration (excluding secrets)")
