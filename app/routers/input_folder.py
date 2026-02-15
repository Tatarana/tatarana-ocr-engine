from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from app.models.responses import OCRResponse
from app.services.ocr_processor import OCRProcessor
from app.services.llm_service import LLMService
from app.services.google_drive import GoogleDriveService
from app.config import GOOGLE_DRIVE_INPUT_FOLDER_ID, GOOGLE_DRIVE_OUTPUT_FOLDER_ID, OPENAI_API_KEY, LLM_MODEL, LLM_BASE_URL, GOOGLE_DRIVE_CREDENTIALS_PATH

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


@router.get("/list-input-files", response_model=List[Dict[str, Any]])
async def list_input_files(drive_service: GoogleDriveService = Depends(get_drive_service)):
    """List all files in the configured input folder."""
    try:
        if not GOOGLE_DRIVE_INPUT_FOLDER_ID:
            raise HTTPException(
                status_code=400, 
                detail="Input folder ID not configured. Set google_drive.input_folder_id in config.yaml"
            )
        
        files = drive_service.list_files_in_folder(GOOGLE_DRIVE_INPUT_FOLDER_ID)
        return files
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing input files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list input files: {str(e)}")


@router.post("/process-input-folder", response_model=Dict[str, Any])
async def process_input_folder(
    drive_service: GoogleDriveService = Depends(get_drive_service),
    ocr_processor: OCRProcessor = Depends(get_ocr_processor)
):
    """Process all files in the configured input folder."""
    try:
        if not GOOGLE_DRIVE_INPUT_FOLDER_ID:
            raise HTTPException(
                status_code=400, 
                detail="Input folder ID not configured. Set google_drive.input_folder_id in config.yaml"
            )
        
        # Get all files in input folder
        files = drive_service.list_files_in_folder(GOOGLE_DRIVE_INPUT_FOLDER_ID)
        
        if not files:
            return {
                "message": "No files found in input folder",
                "processed_files": [],
                "failed_files": []
            }
        
        processed_files = []
        failed_files = []
        
        for file in files:
            try:
                file_id = file['id']
                file_name = file['name']
                
                # Skip non-supported formats
                if not file['name'].lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                    failed_files.append({
                        "file_name": file_name,
                        "error": "Unsupported file format"
                    })
                    continue
                
                # Identify and process file
                identification = ocr_processor.identify_file(file_id)
                bank = identification.get("bank", "unknown").lower()
                document_type = identification.get("document_type", "unknown")
                
                logger.info(f"Processing {file_name}: bank={bank}, type={document_type}")
                
                # Route to appropriate processor
                if document_type == "bank_statement":
                    if bank in ["picpay", "itau"]:
                        result = ocr_processor.process_bank_statement(file_id, bank)
                    else:
                        failed_files.append({
                            "file_name": file_name,
                            "error": f"Unsupported bank for bank statements: {bank}"
                        })
                        continue
                elif document_type == "credit_card":
                    if bank in ["picpay", "itau", "xp"]:
                        result = ocr_processor.process_credit_card_statement(file_id, bank)
                    else:
                        failed_files.append({
                            "file_name": file_name,
                            "error": f"Unsupported bank for credit cards: {bank}"
                        })
                        continue
                else:
                    failed_files.append({
                        "file_name": file_name,
                        "error": f"Unsupported document type: {document_type}"
                    })
                    continue
                
                if result.get("success"):
                    processed_files.append({
                        "file_name": file_name,
                        "csv_file_id": result.get("csv_file_id"),
                        "csv_file_url": result.get("csv_file_url"),
                        "transactions_count": result.get("transactions_count"),
                        "processing_time": result.get("processing_time")
                    })
                else:
                    failed_files.append({
                        "file_name": file_name,
                        "error": result.get("message", "Processing failed")
                    })
                    
            except Exception as e:
                logger.error(f"Error processing file {file.get('name', 'unknown')}: {e}")
                failed_files.append({
                    "file_name": file.get('name', 'unknown'),
                    "error": str(e)
                })
        
        return {
            "message": f"Processed {len(processed_files)} files successfully, {len(failed_files)} files failed",
            "total_files": len(files),
            "processed_files": processed_files,
            "failed_files": failed_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing input folder: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process input folder: {str(e)}")
