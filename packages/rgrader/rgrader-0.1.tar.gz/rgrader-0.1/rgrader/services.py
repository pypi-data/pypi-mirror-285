"""Singletone Google Services"""
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .classroom.connector import ClassroomConnector
from .drive import GoogleDriveService
from .utils import find_descendant

SCOPES = ClassroomConnector.SCOPES + GoogleDriveService.SCOPES


class Auth:

    def __init__(self, credentials_file: str):
        """"""
        self.credentials_file = credentials_file

    def get_credentials(self):
        """Return credentials for all Google Services"""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        try:

            token_path = find_descendant("token.json")

            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            # If there are no (valid) credentials available, let the user log in.
        except FileNotFoundError:
            print("token.json not found")
        finally:
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

        return creds


auth = Auth(find_descendant("credentials.json"))
credentials = auth.get_credentials()

drive_service = GoogleDriveService(credentials=credentials)
classroom_service = ClassroomConnector(credentials=credentials)
