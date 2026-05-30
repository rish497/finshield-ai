FINANCE_WORDS = [
    "bank",
    "money",
    "upi",
    "withdraw",
    "claim",
    "reward",
    "payment",
    "refund",
    "transaction",
    "credit card",
    "loan",
    "otp",
    "account",
    "cashback",
    "kyc"
]


def is_finance_related(message):

    msg = message.lower()

    for word in FINANCE_WORDS:

        if word in msg:
            return True

    return False