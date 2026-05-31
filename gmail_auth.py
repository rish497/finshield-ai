import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def authenticate_gmail():

    token_str = os.getenv("GMAIL_TOKEN")

    if not token_str:
        raise Exception("GMAIL_TOKEN not found in environment variables")

    token_data = json.loads(token_str)

    creds = Credentials.from_authorized_user_info(
        token_data,
        SCOPES
    )

    # refresh if needed
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("gmail", "v1", credentials=creds)

    return service