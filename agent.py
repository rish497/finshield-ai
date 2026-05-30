import os
import base64
import time

import google.generativeai as genai
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from filter import is_finance_related


# -------------------------
# CONFIG
# -------------------------

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# -------------------------
# GMAIL AUTH
# -------------------------

def authenticate_gmail():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

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


# -------------------------
# READ EMAIL BODY
# -------------------------

def get_email_body(payload):

    body = ""

    if "parts" in payload:

        for part in payload["parts"]:

            if part["mimeType"] == "text/plain":

                data = part["body"].get("data")

                if data:
                    body += base64.urlsafe_b64decode(
                        data
                    ).decode("utf-8")

    else:

        data = payload["body"].get("data")

        if data:
            body = base64.urlsafe_b64decode(
                data
            ).decode("utf-8")

    return body


# -------------------------
# GEMINI ANALYSIS
# -------------------------

def analyze_email(subject, body):

    full_text = f"{subject}\n{body}"

    print(f"\nEmail Subject: {subject}")

    if not is_finance_related(full_text):

        print("Not finance-related.")
        print("Agent sleeping.")
        return

    print("Finance-related detected.")
    print("Waking Gemini...\n")

    prompt = f"""
    You are an AI financial fraud detector.

    Analyze this email.

    Subject:
    {subject}

    Body:
    {body}

    Give:
    1. Scam Risk Score (0-100)
    2. Final Verdict
    3. Reasons for suspicion
    """

    response = model.generate_content(prompt)

    print(response.text)


# -------------------------
# MAIN AGENT LOOP
# -------------------------

service = authenticate_gmail()

checked_emails = []

print("FinShield Agent Started...\n")

while True:

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=5
    ).execute()

    messages = results.get("messages", [])

    for msg in messages:

        email_id = msg["id"]

        if email_id not in checked_emails:

            message = service.users().messages().get(
                userId="me",
                id=email_id
            ).execute()

            headers = message["payload"]["headers"]

            subject = "No Subject"

            for header in headers:

                if header["name"] == "Subject":
                    subject = header["value"]

            body = get_email_body(
                message["payload"]
            )

            analyze_email(
                subject,
                body
            )

            checked_emails.append(
                email_id
            )

    print("\nSleeping...\n")

    time.sleep(30)