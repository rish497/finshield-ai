from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

client = MongoClient(
    os.getenv("MONGO_URI")
)

db = client["finshield"]

scam_collection = db["scams"]


def email_already_checked(
    message_id
):

    existing = (
        scam_collection.find_one({
            "message_id":
            message_id
        })
    )

    return existing is not None


def save_scam_email(
    message_id,
    subject,
    sender,
    risk,
    reason,
    category="Phishing"
):

    scam_collection.insert_one({

        "message_id":
        message_id,

        "subject":
        subject,

        "sender":
        sender,

        "risk":
        risk,

        "category":
        category,

        "reason":
        reason,

        "status":
        "flagged",

        "checked_at":
        datetime.now()
    })


def get_dashboard_stats():

    threats = (
        scam_collection
        .count_documents({})
    )

    protected = max(
        threats * 8,
        threats
    )

    if threats >= 8:
        level = "HIGH"

    elif threats >= 4:
        level = "MEDIUM"

    elif threats >= 1:
        level = "LOW"

    else:
        level = "SAFE"

    return {
        "protected":
        protected,

        "threats":
        threats,

        "level":
        level
    }


def get_recent_scams():

    scams = list(

        scam_collection
        .find()

        .sort(
            "_id",
            -1
        )

        .limit(10)

    )

    return scams