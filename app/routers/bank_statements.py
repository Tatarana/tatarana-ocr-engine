from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.requests import BankStatementRequest
from app.models.responses import OCRResponse
from app.services.ocr_processor import OCRProcessor
from app.services.llm_service import LLMService
from app.services.google_drive import GoogleDriveService
from app.config import OPENAI_API_KEY, LLM_MODEL, LLM_BASE_URL, GOOGLE_DRIVE_CREDENTIALS_PATH

logger = logging.getLogger(__name__)

router = APIRouter()


def get_llm_service():
    """Dependency to get LLM service instance."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return LLMService(api_key=OPENAI_API_KEY, model=LLM_MODEL, base_url=LLM_BASE_URL)


def get_drive_service():
    """Dependency to get Google Drive service instance."""
    if not GOOGLE_DRIVE_CREDENTIALS_PATH:
        raise HTTPException(status_code=500, detail="Google Drive credentials not configured")
    return GoogleDriveService(credentials_path=GOOGLE_DRIVE_CREDENTIALS_PATH)


def get_ocr_processor(llm_service=Depends(get_llm_service), drive_service=Depends(get_drive_service)):
    """Dependency to get OCR processor instance."""
    return OCRProcessor(llm_service=llm_service, drive_service=drive_service)


@router.post("/ocr-bank-statement-picpay", response_model=OCRResponse)
async def process_picpay_bank_statement(
    request: BankStatementRequest,
    ocr_processor: OCRProcessor = Depends(get_ocr_processor)
):
    """Process PicPay bank statement."""
    try:
        result = ocr_processor.process_bank_statement(request.file_id, "picpay")
        return OCRResponse(**result)
    except Exception as e:
        logger.error(f"Error processing PicPay bank statement {request.file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process PicPay bank statement: {str(e)}")


@router.post("/ocr-bank-statement-itau", response_model=OCRResponse)
async def process_itau_bank_statement(
    request: BankStatementRequest,
    ocr_processor: OCRProcessor = Depends(get_ocr_processor)
):
    """Process Itaú bank statement."""
    try:
        result = ocr_processor.process_bank_statement(request.file_id, "itau")
        return OCRResponse(**result)
    except Exception as e:
        logger.error(f"Error processing Itaú bank statement {request.file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process Itaú bank statement: {str(e)}")
