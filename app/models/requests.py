from pydantic import BaseModel, Field
from typing import Optional


class OCRFileRequest(BaseModel):
    """Request model for OCR file processing."""
    file_id: str = Field(..., description="Google Drive file ID")
    output_filename: Optional[str] = Field(None, description="Optional output filename")


class IdentifyFileRequest(BaseModel):
    """Request model for file identification."""
    file_id: str = Field(..., description="Google Drive file ID")


class BankStatementRequest(BaseModel):
    """Request model for bank statement processing."""
    file_id: str = Field(..., description="Google Drive file ID")
    output_filename: Optional[str] = Field(None, description="Optional output filename")


class CreditCardRequest(BaseModel):
    """Request model for credit card statement processing."""
    file_id: str = Field(..., description="Google Drive file ID")
    output_filename: Optional[str] = Field(None, description="Optional output filename")
