import google.generativeai as genai
import os

from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def analyze_email(
    subject,
    sender,
    body
):

    prompt = f"""
You are a financial
fraud detection AI.

Analyze this email.

Subject:
{subject}

Sender:
{sender}

Body:
{body}

Determine:

1. Is it a scam?
2. Risk score (0-100)
3. Reason

Respond ONLY in this format:

SCAM: YES or NO
RISK: number
REASON: short reason
"""

    response = model.generate_content(
        prompt
    )

    text = response.text

    is_scam = (
        "SCAM: YES"
        in text.upper()
    )

    risk = 0
    reason = "Unknown"

    lines = text.split("\n")

    for line in lines:

        if "RISK:" in line:

            try:
                risk = int(
                    line
                    .split(":")[1]
                    .strip()
                )
            except:
                pass

        if "REASON:" in line:

            reason = (
                line
                .split(":")[1]
                .strip()
            )

    return {
        "is_scam":
        is_scam,

        "risk":
        risk,

        "reason":
        reason
    }