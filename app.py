import os

from mongo_service import (
    get_dashboard_stats,
    get_recent_scams,
    get_top_scam_category,
    get_average_risk
)

from flask import (
    Flask,
    redirect,
    url_for,
    session,
    render_template
)

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

secret = os.environ.get("SECRET_KEY")
if not secret:
    print("WARNING: SECRET_KEY missing!")
    secret = "temporary-dev-key"

app.secret_key = secret

# -------------------------
# GOOGLE AUTH
# -------------------------

oauth = OAuth(app)

google = oauth.register(
    name="google",

    client_id=os.getenv(
        "GOOGLE_CLIENT_ID"
    ),

    client_secret=os.getenv(
        "GOOGLE_CLIENT_SECRET"
    ),

    server_metadata_url=(
        "https://accounts.google.com/"
        ".well-known/openid-configuration"
    ),

    client_kwargs={
        "scope":
        "openid email profile"
    }
)


# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def home():

    user = session.get(
        "user"
    )

    if user:

        return redirect(
            url_for(
                "dashboard"
            )
        )

    return render_template(
        "login.html"
    )


@app.route("/login")
def login():

    redirect_uri = url_for(
        "authorize",
        _external=True
    )

    return google.authorize_redirect(
        redirect_uri
    )


@app.route("/authorize")
def authorize():

    token = (
        google
        .authorize_access_token()
    )

    user_info = token.get(
        "userinfo"
    )

    session["user"] = {

        "name":
        user_info[
            "name"
        ],

        "email":
        user_info[
            "email"
        ],

        "picture":
        user_info[
            "picture"
        ]
    }

    return redirect(
        url_for(
            "dashboard"
        )
    )


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    # -------------------------
    # DATA FETCH
    # -------------------------

    stats = get_dashboard_stats() or {}

    recent_scams = get_recent_scams() or []

    top_category = get_top_scam_category() or "No Data"

    average_risk = get_average_risk() or 0

    # -------------------------
    # HIGH RISK CALCULATION
    # -------------------------

    high_risk = sum(
        1 for scam in recent_scams
        if scam.get("risk", 0) >= 80
    )

    # -------------------------
    # SAFE STATS EXTRACTION
    # -------------------------

    protected_emails = stats.get(
        "protected_emails",
        stats.get("protected", 0)
    )

    threats_detected = stats.get(
        "threats_detected",
        stats.get("threats", 0)
    )

    # -------------------------
    # THREAT LEVEL (AI SCORE)
    # -------------------------

    threat_level = max(
        0,
        min(
            100,
            100 - (high_risk * 10)
        )
    )

    # -------------------------
    # RENDER
    # -------------------------

    return render_template(

        "dashboard.html",

        user=session["user"],

        protected_emails=protected_emails,

        threats_detected=threats_detected,

        threat_level=threat_level,

        high_risk=high_risk,

        recent_scams=recent_scams,

        top_category=top_category,

        average_risk=average_risk
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for(
            "home"
        )
    )


if __name__ == "__main__":
    app.run(
        debug=True
    )