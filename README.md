# FinShield AI

FinShield AI is an AI-powered Gmail security agent that detects financial scam emails, phishing attempts, fake KYC alerts, reward scams, UPI fraud, impersonation attempts, fake job offers, medical scams, and suspicious financial messages.

Built for the **Google Cloud Rapid Agent Hackathon on Devpost**, FinShield AI goes beyond a normal chatbot. It is an action-taking security agent that connects to Gmail, scans real inbox messages, uses Gemini to reason over scam patterns, stores threat intelligence in MongoDB, labels dangerous emails inside Gmail, and generates personalized threat reports through a MongoDB-powered intelligence layer.

---

## 🌐 Live Demo

Try FinShield AI here:

🔗 https://finshield-ai-bwj2.onrender.com

---

## 🚀 Project Overview

Modern scam emails are becoming harder to detect because attackers use urgency, fear, fake branding, impersonation, and emotional manipulation to trick users into clicking links or giving away sensitive information.

FinShield AI solves this by acting as a personal inbox defense agent.

Once a user logs in with Google, FinShield AI:

1. Authenticates the user securely with Google OAuth.
2. Connects to Gmail using the Gmail API.
3. Scans recent emails for suspicious financial scam patterns.
4. Uses Gemini to analyze subject lines, senders, and email snippets.
5. Classifies emails by scam type, threat type, reason, and risk score.
6. Stores scam detections and user threat history in MongoDB Atlas.
7. Creates and applies a Gmail warning label to risky emails.
8. Displays live threat intelligence inside a Flask dashboard.
9. Generates a personalized threat report using stored MongoDB scam history.

---

## 🧠 What Makes It an Agent?

FinShield AI is not just a chatbot that gives advice. It performs real actions on behalf of the user after the user grants permission.

The agent can:

* Connect to a live Gmail inbox
* Retrieve recent Gmail messages
* Analyze email content with Gemini
* Detect phishing and financial scam patterns
* Decide whether an email is suspicious
* Assign a scam category and risk score
* Save threat intelligence to MongoDB
* Create Gmail labels
* Apply scam warning labels to dangerous emails
* Continuously monitor inbox activity
* Generate personalized threat intelligence reports

This makes FinShield AI an action-taking agent for real-world financial scam prevention.

---

## 🏦 Problem Statement

Financial scams are a major threat to everyday users. People receive fake banking alerts, refund scams, investment fraud messages, KYC update warnings, job scams, phishing links, fake medical alerts, and suspicious reward emails that can look real at first glance.

Scam emails often:

* Create urgency
* Use fear tactics
* Pretend to be banks, Google, hospitals, employers, or government agencies
* Offer fake rewards
* Ask users to verify accounts
* Include suspicious links
* Request money or personal information
* Impersonate trusted brands
* Use unofficial sender addresses

FinShield AI helps users detect these scams before they fall for them.

---

## ✨ Key Features

### 🔐 Google OAuth Login

Users sign in securely with their Google account. FinShield AI uses Google OAuth instead of storing Gmail passwords.

### 📧 Gmail Inbox Scanning

The app uses the Gmail API to fetch recent messages from the authenticated user's inbox.

### 🧠 Gemini-Powered Scam Detection

Gemini analyzes the email subject, sender, and snippet/body preview to detect scam signals such as phishing, urgency, impersonation, suspicious links, fake rewards, emotional manipulation, and money requests.

### 🏷 Automatic Gmail Labeling

If an email is detected as suspicious, FinShield AI creates and applies a Gmail label:

```text
⚠ Financial Scam
```

This makes dangerous emails easier to identify directly inside Gmail.

### 📊 Live Threat Dashboard

The dashboard shows:

* Protected emails
* Threats detected
* High-risk emails
* Top scam category
* Average risk score
* Recent scam detections
* Current threat level
* Gmail account profile
* Threat intelligence feed

### 🧠 MCP Threat Agent

FinShield AI includes an MCP Threat Agent page that generates a personalized security report from stored scam detections.

The report summarizes:

* Overall threat status
* Most common scam patterns
* Highest-risk threats
* Recommended user actions
* MongoDB/MCP integration status

### 🗄 MongoDB Atlas Storage

MongoDB Atlas stores:

* Authenticated user records
* Gmail OAuth token data
* Scam detections
* Risk scores
* Scam categories
* Threat types
* Detection reasons
* Historical threat intelligence

### 🔁 Continuous Background Bot

A background scanner repeatedly checks active users, analyzes new messages, saves scam results, and labels dangerous emails.

---

## 🛠 Tech Stack

### Frontend

* HTML
* CSS
* Jinja templates
* Responsive cybersecurity dashboard UI

### Backend

* Python
* Flask
* Gunicorn
* Authlib
* Python-dotenv

### AI

* Google Gemini API
* Gemini 2.5 Flash for scam classification and threat report generation

### Google Cloud / Google APIs

* Google Cloud Console
* Google OAuth 2.0
* Gmail API
* Gmail label management
* Gmail message modification

### Database

* MongoDB Atlas
* PyMongo
* MongoDB MCP integration code
* PyMongo fallback for deployment stability

### Deployment

* Render
* Gunicorn
* Environment variables
* Optional Node/npm setup for MCP support

---

## 🧩 Architecture

```text
User
 |
 | 1. Logs in with Google
 v
Flask Web App
 |
 | 2. OAuth token stored securely
 v
MongoDB Atlas
 |
 | 3. Background bot loads active users
 v
Gmail API
 |
 | 4. Recent emails are fetched
 v
Gemini AI
 |
 | 5. Email is analyzed for scam risk
 v
MongoDB Atlas
 |
 | 6. Scam result is saved
 v
Gmail API
 |
 | 7. Scam label is applied to risky email
 v
Dashboard
 |
 | 8. User views live threat intelligence
 v
MCP Threat Agent
 |
 | 9. Stored scam history is analyzed into a personalized report
```

---

## 🤖 Agent Workflow

FinShield AI has two main agent workflows.

### 1. Gmail Scam Detection Agent

```text
Gmail API → Gemini scam analysis → MongoDB storage → Gmail scam label
```

This agent scans recent emails, detects scams, stores the results, and labels risky messages.

### 2. Threat Intelligence Agent

```text
MongoDB scam history → Gemini summary → Dashboard report
```

This agent reads stored threat history and generates a clear security report explaining scam patterns and recommended actions.

---

## 🗃 Data Storage

FinShield AI uses MongoDB Atlas as the main database.

### Database Name

```text
finshield
```

### Collections

#### `users`

Stores authenticated users and their Gmail OAuth token data.

Example:

```json
{
  "email": "user@example.com",
  "gmail_token": {
    "token": "ACCESS_TOKEN",
    "refresh_token": "REFRESH_TOKEN",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "GOOGLE_CLIENT_ID",
    "client_secret": "GOOGLE_CLIENT_SECRET",
    "scopes": [
      "openid",
      "email",
      "profile",
      "https://www.googleapis.com/auth/gmail.modify",
      "https://www.googleapis.com/auth/gmail.labels"
    ]
  }
}
```

#### `scams`

Stores scam detection results.

Example:

```json
{
  "user_email": "user@example.com",
  "message_id": "gmail_message_id",
  "subject": "Urgent KYC Update Required",
  "sender": "fake-bank@example.com",
  "risk": 92,
  "category": "Banking Scam",
  "threat_type": "Phishing",
  "reason": "Urgency and suspicious account verification request",
  "status": "flagged",
  "checked_at": "timestamp"
}
```

---

## 🧠 Gemini Scam Detection

Gemini is prompted to behave as a financial fraud detection system.

It checks for:

* Banking scams
* UPI scams
* Investment fraud
* Crypto scams
* Fake refunds
* KYC scams
* Government impersonation
* Medical scams
* Lottery scams
* Job scams
* Phishing attempts
* Identity theft
* General fraud

Gemini returns structured JSON like:

```json
{
  "is_scam": true,
  "risk": 92,
  "category": "Banking Scam",
  "threat_type": "Phishing",
  "reason": "Urgency and fake reward tactic",
  "recommended_action": "Block sender immediately"
}
```

---

## 🧠 MongoDB MCP Integration

FinShield AI includes MongoDB MCP integration code for the hackathon partner track.

The MCP Threat Agent is designed to use MongoDB as an agent-accessible tool layer for reading stored scam intelligence. It attempts to connect to the MongoDB MCP server and query scam history using MCP-style tool calls.

Because MCP stdio behavior can vary across local Windows environments and hosted Python deployments, FinShield AI also includes a PyMongo fallback path. This keeps the deployed Render app stable while preserving the MCP integration code and workflow.

### MCP Behavior

When `USE_MCP=true`, the app attempts to use MongoDB MCP.

When `USE_MCP=false`, the app uses the PyMongo fallback immediately for deployment stability.

Recommended Render setting:

```env
USE_MCP=false
```

Recommended local MCP testing setting:

```env
USE_MCP=true
```

### MCP Threat Agent Flow

```text
MongoDB Atlas scam data
 |
 | Attempt MongoDB MCP query
 v
MCP Threat Agent
 |
 | If MCP is unavailable, use PyMongo fallback
 v
Gemini report generation
 |
 v
Formatted dashboard threat report
```

### Why This Matters

This shows how FinShield AI uses MongoDB not only as a database, but as the foundation for threat intelligence. Stored scam detections become queryable history that the agent can analyze to explain patterns, identify top risks, and recommend protective actions.

---

## 🛡 Security Notes

FinShield AI does not store Gmail passwords.

The app uses:

* Google OAuth 2.0
* Gmail API access tokens
* Refresh tokens
* Environment variables
* MongoDB Atlas
* Server-side session handling


## 🧑‍⚖️ Privacy

FinShield AI only scans emails after the user logs in and grants permission through Google OAuth.

The app processes:

* Email subject
* Sender
* Gmail snippet/body preview
* Gmail message ID
* Scam category
* Risk score
* Detection reason

The app stores only the metadata needed for threat detection, scam labeling, dashboard analytics, and threat intelligence reporting.

---

## 🏆 Hackathon Track

FinShield AI fits the **Financial Services** challenge because it helps protect users from financial fraud, phishing, KYC scams, fake rewards, banking impersonation, job scams, and suspicious money-related emails.

It also aligns with the **MongoDB partner track** by using MongoDB Atlas as the threat intelligence database and including MongoDB MCP integration code for agent-style querying of stored scam history.

---

## 🌍 Potential Impact

FinShield AI can help everyday users avoid financial fraud by providing an automated inbox protection agent.

Potential users include:

* Students
* Senior citizens
* Small business owners
* Online banking users
* UPI users
* People who receive frequent financial emails
* Anyone vulnerable to phishing attacks

By detecting scams early and labeling suspicious emails directly inside Gmail, FinShield AI reduces the chance that users click dangerous links or trust fake messages.

---

## 🔮 Future Improvements

Planned improvements include:

* Full Gmail body parsing
* Real-time push notifications
* Browser extension support
* User-controlled scan settings
* Risk explanation cards
* Scam trend charts
* Multi-language scam detection
* Admin dashboard for families or organizations
* Deeper Google Cloud Agent Builder integration
* Production-stable MCP deployment
* Automatic suspicious-link analysis
* Email quarantine workflow
* Family protection mode for vulnerable users

---

## 🧑‍💻 Built By

Built by **Rishabh Mittal** for the **Google Cloud Rapid Agent Hackathon** on Devpost.

---

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

