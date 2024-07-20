"""Google Drive API client"""
import io
import shutil

import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


class GoogleDriveService(object):
    """Google Drive client"""

    SCOPES = [
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    def __init__(self, credentials):
        self._service = build('drive', 'v3', credentials=credentials)

    def download_file(self, file_id: str, destination: str) -> None:
        """Download file from Google Drive by file_id"""

        request = self._service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        fh.seek(0)
        with open(destination, 'wb') as f:
            shutil.copyfileobj(fh, f, length=131072)

    def _get_credentials(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secret, self.scopes)
        self.creds = flow.run_local_server(port=8080)
        return self.creds
