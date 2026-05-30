import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re

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

You are FinShield AI,
an advanced financial
fraud detection system.

Analyze this email.

EMAIL SUBJECT:
{subject}

SENDER:
{sender}

BODY:
{body}

Detect:

1. Banking scam
2. UPI scam
3. Investment fraud
4. Crypto scam
5. Fake refund
6. KYC scam
7. Government impersonation
8. Medical scam
9. Lottery scam
10. Job scam
11. Phishing attempt
12. Identity theft
13. General fraud

Check for:

- urgency
- fear tactics
- fake rewards
- impersonation
- suspicious links
- money requests
- mismatched sender identity
- emotional manipulation

Respond ONLY in JSON.

Example:

{{
"is_scam": true,
"risk": 92,
"category": "Banking Scam",
"threat_type": "Phishing",
"reason": "Urgency and fake reward tactic",
"recommended_action":
"Block sender immediately"
}}

"""

    response = model.generate_content(
        prompt
    )

    text = response.text.strip()

    text = re.sub(
        r"```json|```",
        "",
        text
    ).strip()

    try:

        result = json.loads(
            text
        )

        return result

    except:

        return {
            "is_scam":
            False,

            "risk":
            0,

            "category":
            "Unknown",

            "threat_type":
            "Unknown",

            "reason":
            "Parsing failed",

            "recommended_action":
            "Manual review"
        }