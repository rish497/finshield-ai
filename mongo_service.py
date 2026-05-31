from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client["finshield"]
scam_collection = db["scams"]


# -------------------------
# CHECK DUPLICATE EMAIL
# -------------------------
def email_already_checked(user_email, message_id):

    return scam_collection.find_one({
        "user_email": user_email,
        "message_id": message_id
    }) is not None


# -------------------------
# SAVE SCAM EMAIL (USER FIX ADDED)
# -------------------------
def save_scam_email(
    user_email,
    message_id,
    subject,
    sender,
    risk,
    reason,
    category,
    threat_type
):
    scam_collection.insert_one({

        "user_email": user_email,   # 👈 CRITICAL FIX

        "message_id": message_id,
        "subject": subject,
        "sender": sender,

        "risk": risk,
        "category": category,
        "threat_type": threat_type,
        "reason": reason,

        "status": "flagged",
        "checked_at": datetime.now()
    })

def get_all_users_with_tokens():
    users = db["users"].find(
        {"gmail_token": {"$exists": True}}
    )

    return list(users)

# -------------------------
# DASHBOARD STATS (USER FILTERED)
# -------------------------
def get_dashboard_stats(user_email):

    threats = scam_collection.count_documents({
        "user_email": user_email
    })

    protected = max(threats * 8, threats)

    if threats >= 8:
        level = "HIGH"
    elif threats >= 4:
        level = "MEDIUM"
    elif threats >= 1:
        level = "LOW"
    else:
        level = "SAFE"

    return {
        "protected_emails": protected,
        "threats_detected": threats,
        "level": level
    }


# -------------------------
# RECENT SCAMS (USER FILTERED)
# -------------------------
def get_recent_scams(user_email):

    return list(
        scam_collection.find({
            "user_email": user_email
        })
        .sort("_id", -1)
        .limit(10)
    )


# -------------------------
# TOP CATEGORY (USER FILTERED)
# -------------------------
def get_top_scam_category(user_email):

    pipeline = [
        {"$match": {"user_email": user_email}},
        {
            "$group": {
                "_id": "$category",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]

    result = list(scam_collection.aggregate(pipeline))

    if result:
        return result[0]["_id"]

    return "No Data"


# -------------------------
# AVERAGE RISK (USER FILTERED)
# -------------------------
def get_average_risk(user_email):

    pipeline = [
        {"$match": {"user_email": user_email}},
        {
            "$group": {
                "_id": None,
                "avgRisk": {"$avg": "$risk"}
            }
        }
    ]

    result = list(scam_collection.aggregate(pipeline))

    if result:
        return round(result[0]["avgRisk"], 1)

    return 0