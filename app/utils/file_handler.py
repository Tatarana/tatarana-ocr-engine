import os
import tempfile
from typing import Union, BinaryIO
from pathlib import Path
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles PDF and image file processing."""
    
    @staticmethod
    def save_temp_file(file_content: bytes, filename: str) -> str:
        """Save file content to temporary location."""
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"ocr_{filename}")
        
        with open(temp_path, 'wb') as f:
            f.write(file_content)
        
        return temp_path
    
    @staticmethod
    def convert_pdf_to_images(pdf_path: str, dpi: int = 300) -> list:
        """Convert PDF to list of PIL Images."""
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
            logger.info(f"Converted PDF to {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
        """Validate file extension."""
        ext = Path(filename).suffix.lower().lstrip('.')
        return ext in allowed_extensions
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary file {file_path}: {e}")
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB."""
        return os.path.getsize(file_path) / (1024 * 1024)
