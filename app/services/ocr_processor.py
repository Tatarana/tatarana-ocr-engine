import time
from typing import Dict, Any, Optional
import logging

from app.services.llm_service import LLMService
from app.services.google_drive import GoogleDriveService
from app.services.csv_generator import CSVGenerator
from app.utils.file_handler import FileHandler
from app.utils.prompt_loader import PromptLoader
from app.config import GOOGLE_DRIVE_OUTPUT_FOLDER_ID

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Main OCR processing service."""
    
    def __init__(self, llm_service: LLMService, drive_service: GoogleDriveService):
        self.llm_service = llm_service
        self.drive_service = drive_service
        self.prompt_loader = PromptLoader()
        self.csv_generator = CSVGenerator()
        self.file_handler = FileHandler()
    
    def identify_file(self, file_id: str) -> Dict[str, Any]:
        """Identify bank and document type from file."""
        try:
            start_time = time.time()
            
            # Download file from Google Drive
            file_content, filename = self.drive_service.download_file(file_id)
            
            # Process file based on type
            if filename.lower().endswith('.pdf'):
                # Convert PDF to images for analysis
                temp_path = self.file_handler.save_temp_file(file_content, filename)
                try:
                    images = self.file_handler.convert_pdf_to_images(temp_path)
                    # Use first page for identification
                    image_bytes = self._image_to_bytes(images[0])
                    response = self.llm_service.analyze_image(
                        image_bytes, 
                        self.prompt_loader.get_prompt('identify_file')
                    )
                finally:
                    self.file_handler.cleanup_temp_file(temp_path)
            else:
                # Process image directly
                response = self.llm_service.analyze_image(
                    file_content,
                    self.prompt_loader.get_prompt('identify_file')
                )
            
            # Parse response
            import json
            try:
                identification = json.loads(response)
            except json.JSONDecodeError:
                # Fallback parsing
                identification = {
                    "bank": "unknown",
                    "document_type": "unknown",
                    "confidence": 0.0
                }
            
            processing_time = time.time() - start_time
            logger.info(f"File identification completed in {processing_time:.2f}s")
            
            return {
                **identification,
                "file_id": file_id,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error identifying file {file_id}: {e}")
            raise
    
    def process_bank_statement(self, file_id: str, bank: str) -> Dict[str, Any]:
        """Process bank statement for specific bank."""
        try:
            start_time = time.time()
            
            # Get appropriate prompt
            prompt_key = f"{bank.lower()}_bank_statement"
            prompt = self.prompt_loader.get_prompt(prompt_key)
            
            # Download and process file
            file_content, filename = self.drive_service.download_file(file_id)
            
            # Extract data using LLM
            if filename.lower().endswith('.pdf'):
                csv_content = self._process_pdf(file_content, filename, prompt)
            else:
                csv_content = self._process_image(file_content, prompt)
            
            # Generate output filename
            output_filename = self.csv_generator.generate_filename(bank, "bank_statement", filename)
            
            # Upload CSV to Google Drive
            csv_file_id, csv_file_url = self.drive_service.upload_csv(
                csv_content, 
                output_filename,
                GOOGLE_DRIVE_OUTPUT_FOLDER_ID  # Use output folder from config
            )
            
            # Count transactions
            lines = csv_content.strip().split('\n')
            transactions_count = max(0, len(lines) - 1)  # Subtract header row
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "message": f"Successfully processed {bank} bank statement",
                "csv_file_id": csv_file_id,
                "csv_file_url": csv_file_url,
                "transactions_count": transactions_count,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing bank statement {file_id}: {e}")
            return {
                "success": False,
                "message": "Failed to process bank statement",
                "error": str(e)
            }
    
    def process_credit_card_statement(self, file_id: str, bank: str) -> Dict[str, Any]:
        """Process credit card statement for specific bank."""
        try:
            start_time = time.time()
            
            # Get appropriate prompt
            prompt_key = f"{bank.lower()}_credit_card"
            prompt = self.prompt_loader.get_prompt(prompt_key)
            
            # Download and process file
            file_content, filename = self.drive_service.download_file(file_id)
            
            # Extract data using LLM
            if filename.lower().endswith('.pdf'):
                csv_content = self._process_pdf(file_content, filename, prompt)
            else:
                csv_content = self._process_image(file_content, prompt)
            
            # Generate output filename
            output_filename = self.csv_generator.generate_filename(bank, "credit_card", filename)
            
            # Upload CSV to Google Drive
            csv_file_id, csv_file_url = self.drive_service.upload_csv(
                csv_content, 
                output_filename,
                GOOGLE_DRIVE_OUTPUT_FOLDER_ID  # Use output folder from config
            )
            
            # Count transactions
            lines = csv_content.strip().split('\n')
            transactions_count = max(0, len(lines) - 1)  # Subtract header row
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "message": f"Successfully processed {bank} credit card statement",
                "csv_file_id": csv_file_id,
                "csv_file_url": csv_file_url,
                "transactions_count": transactions_count,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing credit card statement {file_id}: {e}")
            return {
                "success": False,
                "message": "Failed to process credit card statement",
                "error": str(e)
            }
    
    def _process_pdf(self, file_content: bytes, filename: str, prompt: str) -> str:
        """Process PDF file and return CSV content."""
        temp_path = self.file_handler.save_temp_file(file_content, filename)
        try:
            images = self.file_handler.convert_pdf_to_images(temp_path)
            
            if len(images) == 1:
                # Single page PDF
                image_bytes = self._image_to_bytes(images[0])
                response = self.llm_service.analyze_image(image_bytes, prompt)
            else:
                # Multi-page PDF
                image_bytes_list = [self._image_to_bytes(img) for img in images]
                response = self.llm_service.analyze_multiple_images(image_bytes_list, prompt)
            
            return self.csv_generator.create_csv_from_llm_response(response)
            
        finally:
            self.file_handler.cleanup_temp_file(temp_path)
    
    def _process_image(self, file_content: bytes, prompt: str) -> str:
        """Process image file and return CSV content."""
        response = self.llm_service.analyze_image(file_content, prompt)
        return self.csv_generator.create_csv_from_llm_response(response)
    
    def _image_to_bytes(self, image) -> bytes:
        """Convert PIL Image to bytes."""
        import io
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
