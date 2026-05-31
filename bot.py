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


def run_bot():
    """
    Background Gmail monitoring loop.
    MUST be started from Flask thread, NOT imported directly.
    """

    checked_ids = set()

    print("\n🛡 FinShield AI Running...")

    while True:

        try:

            # -------------------------
            # FETCH EMAILS
            # -------------------------
            service, emails = get_recent_emails()

            # Create Gmail label once per cycle
            label_id = create_label_if_needed(service)

            # -------------------------
            # PROCESS EMAILS
            # -------------------------
            for email in emails:

                message_id = email.get("message_id")
                gmail_id = email.get("id")

                # Skip if already stored in Mongo
                if email_already_checked(message_id):
                    continue

                # Extra in-memory safety (prevents duplicate loop processing)
                if gmail_id in checked_ids:
                    continue

                checked_ids.add(gmail_id)

                print(f"\n🔍 Checking: {email.get('subject', 'No Subject')}")

                # -------------------------
                # SCAM ANALYSIS
                # -------------------------
                result = analyze_email(
                    email.get("subject", ""),
                    email.get("sender", ""),
                    email.get("body", "")
                )

                print("Result:", result)

                # -------------------------
                # IF SCAM DETECTED
                # -------------------------
                if result.get("is_scam"):

                    print("🚨 SCAM DETECTED")

                    save_scam_email(
                        message_id=message_id,
                        subject=email.get("subject", ""),
                        sender=email.get("sender", ""),
                        risk=result.get("risk", 0),
                        reason=result.get("reason", ""),
                        category=result.get("category", ""),
                        threat_type=result.get("threat_type", "")
                    )

                    apply_label(service, gmail_id, label_id)

                    print("✅ Gmail label applied")

            print("\n⏳ Sleeping 30 seconds...\n")
            time.sleep(30)

        except Exception as e:
            print("❌ Bot error:", e)
            time.sleep(30)