import os
from dotenv import load_dotenv
from app.utils.config_loader import ConfigLoader

# Load environment variables
load_dotenv()

# Load configuration
config_loader = ConfigLoader()

# Application settings
APP_NAME = config_loader.get('app.name', 'tatarana-ocr-engine')
APP_VERSION = config_loader.get('app.version', '1.0.0')
DEBUG = config_loader.get('app.debug', False)

# API settings
API_HOST = config_loader.get('api.host', '0.0.0.0')
API_PORT = config_loader.get('api.port', 8000)
API_TIMEOUT = config_loader.get('api.timeout', 300)
MAX_RETRIES = config_loader.get('api.max_retries', 3)
RETRY_DELAY = config_loader.get('api.retry_delay', 1)

# Google Drive settings
GOOGLE_DRIVE_INPUT_FOLDER_ID = config_loader.get('google_drive.input_folder_id', '')
GOOGLE_DRIVE_OUTPUT_FOLDER_ID = config_loader.get('google_drive.output_folder_id', '')
GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', '')
TEMP_DOWNLOAD_PATH = config_loader.get('google_drive.temp_download_path', '/tmp/ocr_downloads')

# LLM settings
LLM_MODEL = config_loader.get('llm.model', 'gpt-4o')
LLM_BASE_URL = config_loader.get('llm.base_url', '') or os.getenv('LLM_BASE_URL', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
LLM_MAX_TOKENS = config_loader.get('llm.max_tokens', 4000)
LLM_TEMPERATURE = config_loader.get('llm.temperature', 0.1)

# Logging
LOG_LEVEL = config_loader.get('logging.level', 'INFO')

# File processing
MAX_FILE_SIZE_MB = config_loader.get('processing.max_file_size_mb', 50)
SUPPORTED_FORMATS = config_loader.get('processing.supported_formats', ['pdf', 'jpg', 'jpeg', 'png'])
PDF_DPI = config_loader.get('processing.pdf_dpi', 300)
