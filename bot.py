import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from mongo_service import (
    get_all_users_with_tokens,
    save_scam_email,
    email_already_checked,
    db,
)
from scam_detector import analyze_email
from gmail_actions import create_label_if_needed, apply_label

REQUIRED_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
]


def get_service_from_token(token_data, user_email=None):
    if not isinstance(token_data, dict):
        raise ValueError("Token is not a dict. Delete this user's old Mongo token and log in again.")

    required_fields = ["token", "token_uri", "client_id", "client_secret"]
    for field in required_fields:
        if not token_data.get(field):
            raise ValueError(f"Missing token field: {field}")

    scopes = token_data.get("scopes") or REQUIRED_GMAIL_SCOPES
    missing_scopes = [scope for scope in REQUIRED_GMAIL_SCOPES if scope not in scopes]
    if missing_scopes:
        raise PermissionError(
            "Stored Google token is missing Gmail scopes: "
            + ", ".join(missing_scopes)
            + ". Delete the old token in MongoDB and log in again."
        )

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=scopes,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        if user_email:
            db["users"].update_one(
                {"email": user_email},
                {"$set": {"gmail_token.token": creds.token}},
            )

    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def run_bot():
    print("\nFinShield AI Multi-User Bot Running...\n", flush=True)

    while True:
        try:
            users = get_all_users_with_tokens()
            print(f"Active users: {len(users)}", flush=True)

            for user in users:
                email = user.get("email")
                token = user.get("gmail_token")
                print(f"\nScanning user: {email}", flush=True)

                if not token:
                    print("No token found", flush=True)
                    continue

                try:
                    service = get_service_from_token(token, email)
                    label_id = create_label_if_needed(service)
                except Exception as exc:
                    print(f"Gmail auth/label error for {email}: {type(exc).__name__}: {exc}", flush=True)
                    continue

                try:
                    results = service.users().messages().list(userId="me", maxResults=5).execute()
                    messages = results.get("messages", [])
                except Exception as exc:
                    print(f"Gmail API list error for {email}: {exc}", flush=True)
                    continue

                for msg in messages:
                    msg_id = msg["id"]

                    if email_already_checked(email, msg_id):
                        continue

                    try:
                        full_msg = service.users().messages().get(userId="me", id=msg_id).execute()
                        headers = full_msg.get("payload", {}).get("headers", [])

                        subject = ""
                        sender = ""
                        for header in headers:
                            name = header.get("name", "").lower()
                            if name == "subject":
                                subject = header.get("value", "")
                            elif name == "from":
                                sender = header.get("value", "")

                        snippet = full_msg.get("snippet", "")
                        result = analyze_email(subject, sender, snippet)
                        print(f"{email} -> {result}", flush=True)

                        if result.get("is_scam"):
                            save_scam_email(
                                user_email=email,
                                message_id=msg_id,
                                subject=subject,
                                sender=sender,
                                risk=result.get("risk", 0),
                                reason=result.get("reason", ""),
                                category=result.get("category", "Unknown"),
                                threat_type=result.get("threat_type", "Unknown"),
                            )
                            apply_label(service, msg_id, label_id)
                            print("Scam marked", flush=True)

                    except Exception as exc:
                        print(f"Error processing email {msg_id}: {exc}", flush=True)
                        continue

            print("\nSleeping 30 seconds...\n", flush=True)
            time.sleep(30)

        except Exception as exc:
            print(f"\nBOT ERROR: {type(exc).__name__}: {exc}", flush=True)
            time.sleep(30)


if __name__ == "__main__":
    run_bot()
