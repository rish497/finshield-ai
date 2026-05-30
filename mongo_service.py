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
    category,
    threat_type
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

        "threat_type":
        threat_type,

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

def get_top_scam_category():

    pipeline = [

        {
            "$group": {
                "_id":
                "$category",

                "count":
                {
                    "$sum": 1
                }
            }
        },

        {
            "$sort": {
                "count": -1
            }
        },

        {
            "$limit": 1
        }
    ]

    result = list(
        scam_collection.aggregate(
            pipeline
        )
    )

    if result:

        return result[
            0
        ][
            "_id"
        ]

    return "No Data"


def get_average_risk():

    pipeline = [

        {
            "$group": {

                "_id":
                None,

                "avgRisk":
                {
                    "$avg":
                    "$risk"
                }
            }
        }
    ]

    result = list(

        scam_collection
        .aggregate(
            pipeline
        )

    )

    if result:

        return round(
            result[0][
                "avgRisk"
            ],
            1
        )

    return 0