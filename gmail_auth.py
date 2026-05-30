import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

BASE_DIR = os.path.dirname(__file__)
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")


def authenticate_gmail():

    creds = None

    # -------------------------
    # LOAD EXISTING TOKEN
    # -------------------------
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(
            TOKEN_PATH,
            SCOPES
        )

    # -------------------------
    # REFRESH IF POSSIBLE
    # -------------------------
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print("Token refresh failed:", e)
            creds = None

    # -------------------------
    # CRITICAL PRODUCTION CHECK
    # -------------------------
    if not creds or not creds.valid:
        raise Exception(
            "No valid Gmail token found. "
            "Run OAuth locally once and upload token.json to Railway."
        )

    # -------------------------
    # BUILD SERVICE
    # -------------------------
    return build("gmail", "v1", credentials=creds)


if __name__ == "__main__":
    service = authenticate_gmail()
    print("Gmail connected successfully!")