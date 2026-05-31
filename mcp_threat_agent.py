import os
import json
import asyncio
from dotenv import load_dotenv

import google.generativeai as genai

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


DATABASE_NAME = "finshield"
SCAMS_COLLECTION = "scams"


def _extract_text_from_mcp_result(result):
    """
    MCP tool results may return content blocks.
    This helper turns them into plain text safely.
    """

    if not result:
        return ""

    content = getattr(result, "content", None)

    if not content:
        return str(result)

    parts = []

    for item in content:
        text = getattr(item, "text", None)

        if text:
            parts.append(text)
        else:
            parts.append(str(item))

    return "\n".join(parts)


async def _call_mongodb_mcp_tool(tool_name, arguments):
    """
    Starts the official MongoDB MCP server through npx,
    connects to it as an MCP client, and calls one MongoDB tool.

    This is the hackathon partner integration layer.
    """

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise RuntimeError("MONGO_URI is missing from environment variables.")

    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "mongodb-mcp-server@latest",
            "--readOnly"
        ],
        env={
            "MDB_MCP_CONNECTION_STRING": mongo_uri,
            "MDB_MCP_READ_ONLY": "true"
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments
            )

            return _extract_text_from_mcp_result(result)


async def get_mcp_threat_context(user_email):
    """
    Uses MongoDB MCP tools to query stored scam intelligence.

    This does not use PyMongo directly.
    It queries MongoDB through the MongoDB MCP server.
    """

    if not user_email:
        raise ValueError("user_email is required")

    # 1. Recent scams for this user
    recent_scams_raw = await _call_mongodb_mcp_tool(
        "find",
        {
            "database": DATABASE_NAME,
            "collection": SCAMS_COLLECTION,
            "filter": {
                "user_email": user_email
            },
            "sort": {
                "checked_at": -1
            },
            "limit": 10
        }
    )

    # 2. Scam category summary
    category_summary_raw = await _call_mongodb_mcp_tool(
        "aggregate",
        {
            "database": DATABASE_NAME,
            "collection": SCAMS_COLLECTION,
            "pipeline": [
                {
                    "$match": {
                        "user_email": user_email
                    }
                },
                {
                    "$group": {
                        "_id": "$category",
                        "count": {
                            "$sum": 1
                        },
                        "average_risk": {
                            "$avg": "$risk"
                        },
                        "max_risk": {
                            "$max": "$risk"
                        }
                    }
                },
                {
                    "$sort": {
                        "count": -1
                    }
                }
            ]
        }
    )

    # 3. High-risk emails
    high_risk_raw = await _call_mongodb_mcp_tool(
        "find",
        {
            "database": DATABASE_NAME,
            "collection": SCAMS_COLLECTION,
            "filter": {
                "user_email": user_email,
                "risk": {
                    "$gte": 80
                }
            },
            "sort": {
                "risk": -1
            },
            "limit": 5
        }
    )

    return {
        "recent_scams": recent_scams_raw,
        "category_summary": category_summary_raw,
        "high_risk": high_risk_raw
    }


def generate_threat_intelligence_summary(user_email):
    """
    Main function used by Flask.

    It uses MongoDB MCP to retrieve threat data,
    then Gemini turns that MCP data into a human-readable agent summary.
    """

    context = asyncio.run(
        get_mcp_threat_context(user_email)
    )

    prompt = f"""
You are FinShield AI's Threat Intelligence Agent.

You are analyzing scam detection history for this Gmail user:

USER:
{user_email}

The following threat data was retrieved from MongoDB using the official MongoDB MCP server.

RECENT SCAMS:
{context["recent_scams"]}

CATEGORY SUMMARY:
{context["category_summary"]}

HIGH RISK EMAILS:
{context["high_risk"]}

Create a concise threat intelligence report.

Return clean text with these sections:

1. Overall threat status
2. Most common scam patterns
3. Highest risk threats
4. Recommended user actions
5. One-line hackathon explanation of how MongoDB MCP is being used

Keep it clear, impressive, and dashboard-friendly.
"""

    response = model.generate_content(prompt)

    return response.text.strip()


if __name__ == "__main__":
    email = input("Enter user email to analyze with MongoDB MCP: ").strip()

    summary = generate_threat_intelligence_summary(email)

    print("\n===== FinShield MCP Threat Intelligence Report =====\n")
    print(summary)