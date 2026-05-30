from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]


def get_dashboard_stats():

    creds = Credentials.from_authorized_user_file(
        "token.json",
        SCOPES
    )

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    results = service.users().messages().list(
        userId="me",
        maxResults=500
    ).execute()

    messages = results.get(
        "messages",
        []
    )

    protected_emails = len(
        messages
    )

    labels = service.users().labels().list(
        userId="me"
    ).execute()

    scam_label_id = None

    for label in labels.get(
        "labels",
        []
    ):

        if label["name"] == (
            "⚠ Financial Scam"
        ):

            scam_label_id = label[
                "id"
            ]

    threats_detected = 0

    if scam_label_id:

        threats = service.users().messages().list(
            userId="me",
            labelIds=[
                scam_label_id
            ]
        ).execute()

        threats_detected = len(
            threats.get(
                "messages",
                []
            )
        )

    return {
        "protected_emails":
        protected_emails,

        "threats_detected":
        threats_detected
    }