from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.requests import OCRFileRequest, IdentifyFileRequest
from app.models.responses import IdentifyFileResponse, OCRResponse
from app.services.ocr_processor import OCRProcessor
from app.services.llm_service import LLMService
from app.services.google_drive import GoogleDriveService
from app.config import OPENAI_API_KEY, LLM_MODEL, LLM_BASE_URL, GOOGLE_DRIVE_CREDENTIALS_PATH, GOOGLE_DRIVE_FOLDER_ID

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


@router.post("/identify-file", response_model=IdentifyFileResponse)
async def identify_file(
    request: IdentifyFileRequest,
    ocr_processor: OCRProcessor = Depends(get_ocr_processor)
):
    """Identify bank and document type from file."""
    try:
        result = ocr_processor.identify_file(request.file_id)
        
        return IdentifyFileResponse(
            bank=result.get("bank", "unknown"),
            document_type=result.get("document_type", "unknown"),
            confidence=result.get("confidence", 0.0),
            file_id=request.file_id
        )
        
    except Exception as e:
        logger.error(f"Error identifying file {request.file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to identify file: {str(e)}")


@router.post("/ocr-file", response_model=OCRResponse)
async def ocr_file(
    request: OCRFileRequest,
    ocr_processor: OCRProcessor = Depends(get_ocr_processor)
):
    """Main orchestration endpoint for OCR processing."""
    try:
        # First identify the file
        identification = ocr_processor.identify_file(request.file_id)
        bank = identification.get("bank", "unknown").lower()
        document_type = identification.get("document_type", "unknown")
        
        logger.info(f"Identified file: bank={bank}, type={document_type}")
        
        # Route to appropriate processor
        if document_type == "bank_statement":
            if bank in ["picpay", "itau"]:
                result = ocr_processor.process_bank_statement(request.file_id, bank)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported bank for bank statements: {bank}"
                )
        elif document_type == "credit_card":
            if bank in ["picpay", "itau", "xp"]:
                result = ocr_processor.process_credit_card_statement(request.file_id, bank)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported bank for credit cards: {bank}"
                )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported document type: {document_type}"
            )
        
        return OCRResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file {request.file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
