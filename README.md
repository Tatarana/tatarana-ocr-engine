# Tatarana OCR Engine

A Python backend microservice that processes bank and credit card statements from Google Drive using LLM-based OCR and outputs CSV files back to Google Drive.

## Features

- **Multi-bank support**: PicPay, Itaú, and XP statements
- **Document types**: Bank statements and credit card statements
- **LLM-powered OCR**: Uses OpenAI GPT-4o for accurate text extraction
- **Google Drive integration**: Download files and upload CSV results
- **RESTful API**: Clean FastAPI endpoints with automatic OpenAPI documentation
- **Docker support**: Containerized deployment with health checks
- **Configuration-driven**: External YAML configuration for prompts and settings

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Google Drive service account credentials
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Tatarana/tatarana-ocr-engine.git
   cd tatarana-ocr-engine
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google Drive**
   - Place your service account JSON file at `credentials/service-account.json`
   - Set the `GOOGLE_DRIVE_FOLDER_ID` in your `.env` file

### Running the Application

#### Option 1: Docker Compose (Recommended)

```bash
docker-compose up --build
```

The service will be available at `http://localhost:8000`

#### Option 2: Local Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Main Endpoints

#### `POST /api/v1/ocr-file`
Main orchestration endpoint that automatically identifies the file type and routes to the appropriate processor.

**Request:**
```json
{
  "file_id": "your_google_drive_file_id",
  "output_filename": "optional_custom_name.csv"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed PicPay bank statement",
  "csv_file_id": "generated_csv_file_id",
  "csv_file_url": "https://drive.google.com/file/d/...",
  "transactions_count": 25,
  "processing_time_seconds": 12.5
}
```

#### `POST /api/v1/identify-file`
Identifies the bank and document type from a file.

**Request:**
```json
{
  "file_id": "your_google_drive_file_id"
}
```

**Response:**
```json
{
  "bank": "picpay",
  "document_type": "bank_statement",
  "confidence": 0.95,
  "file_id": "your_google_drive_file_id"
}
```

### Input Folder Endpoints

#### `GET /api/v1/list-input-files`
List all files in the configured input folder.

**Response:**
```json
[
  {
    "id": "file_id",
    "name": "statement.pdf",
    "mimeType": "application/pdf",
    "size": "1024000",
    "createdTime": "2023-01-01T12:00:00.000Z"
  }
]
```

#### `POST /api/v1/process-input-folder`
Process all files in the configured input folder automatically.

**Response:**
```json
{
  "message": "Processed 5 files successfully, 1 files failed",
  "total_files": 6,
  "processed_files": [
    {
      "file_name": "picpay_statement.pdf",
      "csv_file_id": "generated_csv_id",
      "csv_file_url": "https://drive.google.com/file/d/...",
      "transactions_count": 25,
      "processing_time": 12.5
    }
  ],
  "failed_files": [
    {
      "file_name": "unsupported_file.txt",
      "error": "Unsupported file format"
    }
  ]
}
```

### Bank-Specific Endpoints

#### Bank Statements
- `POST /api/v1/ocr-bank-statement-picpay`
- `POST /api/v1/ocr-bank-statement-itau`

#### Credit Card Statements
- `POST /api/v1/ocr-cc-statement-picpay`
- `POST /api/v1/ocr-cc-statement-itau`
- `POST /api/v1/ocr-cc-statement-xp`

### System Endpoints

#### `GET /api/v1/health`
Health check endpoint.

#### `GET /api/v1/show-config`
Displays current configuration (excluding secrets).

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Google Drive Configuration
GOOGLE_DRIVE_CREDENTIALS_PATH=./credentials/service-account.json
GOOGLE_DRIVE_FOLDER_ID=your_output_folder_id

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
LLM_BASE_URL=  # Optional: for alternative LLM providers
```

### Application Configuration

Edit `config/config.yaml` to customize:

- API settings (host, port, timeouts)
- LLM model and parameters
- File processing limits
- Logging configuration
- **Input folder ID** (optional, for batch processing)
- **Output folder ID** (required for CSV uploads)

### Prompt Configuration

Edit `config/prompts.yaml` to customize OCR prompts for different banks and document types.

## Supported File Formats

- PDF files (multi-page supported)
- Image files: JPG, JPEG, PNG

## CSV Output Format

The generated CSV files include standardized columns:

| Column | Description |
|--------|-------------|
| date | Transaction date (YYYY-MM-DD) |
| description | Transaction description or merchant name |
| amount | Transaction amount (positive for credits, negative for debits) |
| balance | Account balance (if available) |
| category | Transaction category (if identifiable) |
| installments | Installment information for credit cards (if applicable) |

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

```
tatarana-ocr-engine/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models/              # Pydantic models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic services
│   └── utils/               # Utility functions
├── config/                  # Configuration files
├── tests/                   # Test suite
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── requirements.txt        # Python dependencies
```

## Error Handling

The API provides comprehensive error handling with meaningful error messages:

- **400 Bad Request**: Invalid input parameters or unsupported file types
- **401 Unauthorized**: Missing or invalid API credentials
- **404 Not Found**: File not found in Google Drive
- **429 Too Many Requests**: Rate limiting from external APIs
- **500 Internal Server Error**: Processing failures or system errors

## Monitoring and Logging

- Structured logging with configurable levels
- Health check endpoint for monitoring
- Processing time tracking for performance analysis
- Error tracking with detailed context

## Security Considerations

- API keys and credentials are loaded from environment variables
- No sensitive information is exposed in API responses
- Google Drive service account follows principle of least privilege
- Input validation on all endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for detailed error information
