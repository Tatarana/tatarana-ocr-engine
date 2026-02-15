import os
import tempfile
from typing import Optional, BinaryIO
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import logging

logger = logging.getLogger(__name__)


class GoogleDriveService:
    """Service for interacting with Google Drive API."""
    
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Drive API."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("Successfully authenticated with Google Drive API")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Drive: {e}")
            raise
    
    def download_file(self, file_id: str) -> tuple[bytes, str]:
        """Download file from Google Drive."""
        try:
            # Get file metadata
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields='name, mimeType'
            ).execute()
            
            filename = file_metadata['name']
            logger.info(f"Downloading file: {filename}")
            
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            file_content = bytearray()
            
            downloader = MediaIoBaseDownload(None, request)
            done = False
            
            with tempfile.NamedTemporaryFile() as temp_file:
                downloader = MediaIoBaseDownload(temp_file, request)
                done = False
                
                while done is False:
                    status, done = downloader.next_chunk()
                    logger.debug(f"Download {int(status.progress() * 100)}%.")
                
                temp_file.seek(0)
                file_content = temp_file.read()
            
            return bytes(file_content), filename
            
        except HttpError as e:
            logger.error(f"Google Drive API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            raise
    
    def upload_csv(self, csv_content: str, filename: str, folder_id: Optional[str] = None) -> tuple[str, str]:
        """Upload CSV file to Google Drive."""
        try:
            from googleapiclient.http import MediaIoBaseUpload
            import io
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'mimeType': 'text/csv'
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(csv_content.encode('utf-8-sig')),
                mimetype='text/csv',
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()
            
            file_id = file.get('id')
            web_view_link = file.get('webViewLink')
            
            logger.info(f"Successfully uploaded CSV file: {filename} (ID: {file_id})")
            return file_id, web_view_link
            
        except HttpError as e:
            logger.error(f"Google Drive API error during upload: {e}")
            raise
        except Exception as e:
            logger.error(f"Error uploading CSV file: {e}")
            raise
    
    def list_files_in_folder(self, folder_id: str) -> list:
        """List all files in a specific Google Drive folder."""
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType, size, createdTime)",
                pageSize=1000
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files in folder")
            return files
            
        except HttpError as e:
            logger.error(f"Error listing files in folder: {e}")
            raise
    
    def get_file_info(self, file_id: str) -> dict:
        """Get file information from Google Drive."""
        try:
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields='name, mimeType, size, createdTime, modifiedTime'
            ).execute()
            return file_metadata
        except HttpError as e:
            logger.error(f"Error getting file info: {e}")
            raise
