from gmail_auth import (
    authenticate_gmail
)


def get_recent_emails():

    service = (
        authenticate_gmail()
    )

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

    messages = results.get(
        "messages",
        []
    )

    email_data = []

    for msg in messages:

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

        headers = (
            message[
                "payload"
            ]["headers"]
        )

        subject = ""
        sender = ""

        for header in headers:

            if (
                header["name"]
                ==
                "Subject"
            ):

                subject = (
                    header["value"]
                )

            if (
                header["name"]
                ==
                "From"
            ):

                sender = (
                    header["value"]
                )

        body = ""

        if "snippet" in message:
            body = (
                message["snippet"]
            )

        email_data.append({

            "id":
            msg["id"],

            "message_id":
            msg["id"],

            "subject":
            subject,

            "sender":
            sender,

            "body":
            body
        })

    return (
        service,
        email_data
    )