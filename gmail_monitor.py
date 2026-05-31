from gmail_auth import authenticate_gmail


def get_recent_emails():

    service = authenticate_gmail()

    # -------------------------
    # DEBUG: Gmail ACCOUNT INFO
    # -------------------------
    try:
        profile = service.users().getProfile(userId="me").execute()

        print("\n📧 GMAIL ACCOUNT ACTIVE")
        print("Email:", profile.get("emailAddress"))
        print("Messages Total:", profile.get("messagesTotal"))
        print("----------------------------\n")

    except Exception as e:
        print("⚠️ Could not fetch Gmail profile:", e)

    # -------------------------
    # FETCH EMAIL LIST
    # -------------------------
    print("📡 Fetching latest emails...")

    results = (
        service
        .users()
        .messages()
        .list(
            userId="me",
            maxResults=5
        )
        .execute()
    )

    messages = results.get("messages", [])

    print(f"📬 Messages found: {len(messages)}")

    email_data = []

    # -------------------------
    # PROCESS EACH EMAIL
    # -------------------------
    for i, msg in enumerate(messages, start=1):

        print(f"\n📩 Processing email {i}/{len(messages)}")
        print("Gmail Message ID:", msg["id"])

        message = (
            service
            .users()
            .messages()
            .get(
                userId="me",
                id=msg["id"]
            )
            .execute()
        )

        headers = message.get("payload", {}).get("headers", [])

        subject = ""
        sender = ""

        for header in headers:

            if header.get("name") == "Subject":
                subject = header.get("value", "")

            if header.get("name") == "From":
                sender = header.get("value", "")

        body = message.get("snippet", "")

        print("📌 Subject:", subject)
        print("📨 Sender:", sender)
        print("📝 Snippet:", body[:80])

        email_data.append({

            "id": msg["id"],
            "message_id": msg["id"],
            "subject": subject,
            "sender": sender,
            "body": body
        })

    print("\n✅ Email fetch complete\n")

    return service, email_data