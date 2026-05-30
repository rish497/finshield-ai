from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path

# Gmail read-only permission
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():

    creds = None

    # token.json stores login session
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # If no valid login exists
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_latest_emails():

    service = authenticate_gmail()

    results = service.users().messages().list(
        userId="me",
        maxResults=5
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        print("No emails found.")
        return

    print("\nLatest Emails:\n")

    for msg in messages:

        message = service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()

        headers = message["payload"]["headers"]

        subject = "No Subject"

        for header in headers:
            if header["name"] == "Subject":
                subject = header["value"]

        print(f"Subject: {subject}")


get_latest_emails()