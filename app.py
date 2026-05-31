import os
import threading

from mcp_threat_agent import generate_threat_intelligence_summary
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, session, render_template
import markdown
import bot
from mongo_service import db
from mongo_service import (
    get_dashboard_stats,
    get_recent_scams,
    get_top_scam_category,
    get_average_risk,
)

load_dotenv()

GMAIL_SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
]

app = Flask(__name__)

secret = os.getenv("SECRET_KEY")
if not secret:
    raise RuntimeError("SECRET_KEY not set in environment")
app.secret_key = secret

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": " ".join(GMAIL_SCOPES)},
)

_bot_started = False


def start_bot_once():
    """Start the scanner once per process. Render should run one gunicorn worker."""
    global _bot_started
    if _bot_started or os.getenv("RUN_BOT", "true").lower() != "true":
        return
    _bot_started = True
    threading.Thread(target=bot.run_bot, daemon=True).start()


start_bot_once()


@app.route("/")
def home():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return google.authorize_redirect(
        redirect_uri,
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )


@app.route("/authorize")
def authorize():
    token = google.authorize_access_token()
    user_info = token.get("userinfo") or google.userinfo()

    email = user_info["email"]

    session["user"] = {
        "name": user_info.get("name", email),
        "email": email,
        "picture": user_info.get("picture", ""),
    }

    token_scopes = token.get("scope")
    if isinstance(token_scopes, str):
        token_scopes = token_scopes.split()
    if not token_scopes:
        token_scopes = GMAIL_SCOPES

    token_data = {
        "token": token.get("access_token"),
        "refresh_token": token.get("refresh_token"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "scopes": token_scopes,
    }

    token_data = {k: v for k, v in token_data.items() if v}

    db["users"].update_one(
        {"email": email},
        {"$set": {"gmail_token": token_data, "email": email}},
        upsert=True,
    )

    return redirect(url_for("dashboard"))

@app.route("/mcp-threat-agent")
def mcp_threat_agent():
    if "user" not in session:
        return redirect("/")

    return render_template(
        "mcp_agent.html",
        user=session["user"],
        report=None,
        error=None
    )


@app.route("/mcp-threat-agent/run")
def run_mcp_threat_agent():
    if "user" not in session:
        return redirect("/")

    user_email = session["user"]["email"]

    try:
        report = generate_threat_intelligence_summary(user_email)

        report_html = markdown.markdown(
            report,
            extensions=["extra", "nl2br"]
        )

        error = None

    except Exception as e:
        report_html = None
        error = str(e)

    return render_template(
        "mcp_agent.html",
        user=session["user"],
        report=report_html,
        error=error
    )

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    user_email = session["user"]["email"]

    stats = get_dashboard_stats(user_email)
    recent_scams = get_recent_scams(user_email)
    top_category = get_top_scam_category(user_email)
    average_risk = get_average_risk(user_email)

    high_risk = sum(1 for scam in recent_scams if scam.get("risk", 0) >= 80)

    return render_template(
        "dashboard.html",
        user=session["user"],
        protected_emails=stats.get("protected_emails", 0),
        threats_detected=stats.get("threats_detected", 0),
        threat_level=stats.get("level", "SAFE"),
        high_risk=high_risk,
        recent_scams=recent_scams,
        top_category=top_category,
        average_risk=average_risk,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
