import time

from mongo_service import (
    save_scam_email,
    email_already_checked
)

from gmail_monitor import (
    get_recent_emails
)

from scam_detector import (
    analyze_email
)

from gmail_actions import (
    create_label_if_needed,
    apply_label
)

checked_ids = set()


print(
    "\n🛡 FinShield AI Running..."
)


while True:

    try:

        service, emails = (
            get_recent_emails()
        )

        label_id = (
            create_label_if_needed(
                service
            )
        )

        for email in emails:

            message_id = email[
                "message_id"
            ]

            if (
                email_already_checked(
                    message_id
                )
            ):

                print(
                    "⏭ Already checked"
                )

                continue

            if (
                email["id"]
                in checked_ids
            ):

                continue

            checked_ids.add(
                email["id"]
            )

            print(
                f"\nChecking:"
                f" {email['subject']}"
            )

            result = (
                analyze_email(
                    email[
                        "subject"
                    ],

                    email[
                        "sender"
                    ],

                    email[
                        "body"
                    ]
                )
            )

            print(result)

            if (
                result[
                    "is_scam"
                ]
            ):

                print(
                    "🚨 SCAM DETECTED"
                )
                save_scam_email(

                    message_id=
                    email[
                        "message_id"
                    ],

                    subject=
                    email[
                        "subject"
                    ],

                    sender=
                    email[
                        "sender"
                    ],

                    risk=
                    result[
                        "risk"
                    ],

                    reason=
                    result[
                        "reason"
                    ]
                )

                apply_label(
                    service,

                    email["id"],

                    label_id
                )

                print(
                    "✅ Gmail label added"
                )

        print(
            "\nSleeping..."
        )

        time.sleep(30)

    except Exception as e:

        print(
            "Error:",
            e
        )

        time.sleep(30)