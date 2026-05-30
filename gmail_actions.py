def create_label_if_needed(
    service
):

    labels = (
        service
        .users()
        .labels()
        .list(
            userId="me"
        )
        .execute()
    )

    for label in (
        labels.get(
            "labels",
            []
        )
    ):

        if (
            label["name"]
            ==
            "⚠ Financial Scam"
        ):

            return label["id"]

    label_body = {
        "name":
        "⚠ Financial Scam",

        "labelListVisibility":
        "labelShow",

        "messageListVisibility":
        "show"
    }

    created = (
        service
        .users()
        .labels()
        .create(
            userId="me",
            body=label_body
        )
        .execute()
    )

    return created["id"]


def apply_label(
    service,
    message_id,
    label_id
):

    service.users().messages().modify(
        userId="me",

        id=message_id,

        body={
            "addLabelIds":
            [label_id]
        }
    ).execute()