import os
import json
import asyncio
import traceback
import sys
from datetime import datetime
from dotenv import load_dotenv

import google.generativeai as genai
from pymongo import MongoClient

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

DATABASE_NAME = "finshield"
SCAMS_COLLECTION = "scams"


def _format_exception(e):
    lines = [
        f"Error type: {type(e).__name__}",
        f"Error message: {str(e)}",
        "",
        "Full traceback:",
        traceback.format_exc()
    ]

    if hasattr(e, "exceptions"):
        lines.append("")
        lines.append("Sub-exceptions:")

        for index, sub_error in enumerate(e.exceptions, start=1):
            lines.append(f"\nSub-error {index}:")
            lines.append(f"Type: {type(sub_error).__name__}")
            lines.append(f"Message: {str(sub_error)}")
            lines.append("Traceback:")
            lines.append("".join(traceback.format_exception(sub_error)))

    return "\n".join(lines)


def _extract_text_from_mcp_result(result):
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


def _server_params():
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise RuntimeError("MONGO_URI is missing from environment variables.")

    # MongoDB MCP server is configured through env vars.
    # Official package runs via npx mongodb-mcp-server@latest.
    return StdioServerParameters(
        command="cmd" if sys.platform.startswith("win") else "npx",
        args=[
            "/c",
            "npx",
            "-y",
            "mongodb-mcp-server@latest"
        ] if sys.platform.startswith("win") else [
            "-y",
            "mongodb-mcp-server@latest"
        ],
        env={
            **os.environ,
            "MDB_MCP_CONNECTION_STRING": mongo_uri,
            "MDB_MCP_READ_ONLY": "true"
        }
    )


async def _list_mcp_tools():
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.list_tools()


async def _call_mongodb_mcp_tool(tool_name, arguments):
    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            available_tool_names = [tool.name for tool in tools.tools]

            if tool_name not in available_tool_names:
                raise RuntimeError(
                    f"MCP tool '{tool_name}' was not found. "
                    f"Available tools: {available_tool_names}"
                )

            result = await session.call_tool(tool_name, arguments)

            return _extract_text_from_mcp_result(result)


async def get_mcp_threat_context(user_email):
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
        "source": "MongoDB MCP",
        "recent_scams": recent_scams_raw,
        "category_summary": category_summary_raw,
        "high_risk": high_risk_raw
    }


def get_pymongo_fallback_context(user_email):
    """
    Fallback used when local Windows MCP stdio fails.
    This keeps the demo app working while still preserving the MCP integration code.
    """

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise RuntimeError("MONGO_URI is missing from environment variables.")

    client = MongoClient(mongo_uri)
    db = client[DATABASE_NAME]
    scams = db[SCAMS_COLLECTION]

    recent_scams = list(
        scams.find(
            {"user_email": user_email},
            {
                "_id": 0,
                "subject": 1,
                "sender": 1,
                "risk": 1,
                "category": 1,
                "threat_type": 1,
                "reason": 1,
                "checked_at": 1
            }
        )
        .sort("checked_at", -1)
        .limit(10)
    )

    category_summary = list(
        scams.aggregate(
            [
                {"$match": {"user_email": user_email}},
                {
                    "$group": {
                        "_id": "$category",
                        "count": {"$sum": 1},
                        "average_risk": {"$avg": "$risk"},
                        "max_risk": {"$max": "$risk"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
        )
    )

    high_risk = list(
        scams.find(
            {
                "user_email": user_email,
                "risk": {"$gte": 80}
            },
            {
                "_id": 0,
                "subject": 1,
                "sender": 1,
                "risk": 1,
                "category": 1,
                "threat_type": 1,
                "reason": 1
            }
        )
        .sort("risk", -1)
        .limit(5)
    )

    client.close()

    return {
        "source": "PyMongo fallback because local MCP stdio failed",
        "recent_scams": recent_scams,
        "category_summary": category_summary,
        "high_risk": high_risk
    }


def _json_safe(data):
    def default_converter(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    return json.dumps(data, indent=2, default=default_converter)


def test_mcp_connection():
    try:
        print("Starting MongoDB MCP connection test...")

        tools = asyncio.run(
            asyncio.wait_for(
                _list_mcp_tools(),
                timeout=25
            )
        )

        tool_names = [tool.name for tool in tools.tools]

        return (
            "MongoDB MCP connection successful.\n\n"
            "Available tools:\n"
            + "\n".join(tool_names)
        )

    except asyncio.TimeoutError:
        return (
            "MongoDB MCP connection timed out after 25 seconds.\n\n"
            "The MCP server did not respond in time."
        )

    except Exception as e:
        return _format_exception(e)


def generate_threat_intelligence_summary(user_email):
    """
    Main Flask function.

    On local demo, USE_MCP=true tries MongoDB MCP.
    On Render, USE_MCP=false skips MCP and uses PyMongo fallback immediately
    so the deployed app stays fast and stable.
    """

    use_mcp = os.getenv("USE_MCP", "false").lower() == "true"

    if use_mcp:
        try:
            context = asyncio.run(
                asyncio.wait_for(
                    get_mcp_threat_context(user_email),
                    timeout=20
                )
            )

            mcp_status = (
                "MongoDB MCP succeeded. Scam history was queried through MongoDB MCP tools."
            )

        except Exception as e:
            mcp_status = (
                "MongoDB MCP was attempted but failed in this environment. "
                "The app used a PyMongo fallback so the report could still be generated.\n\n"
                "MCP error:\n"
                + _format_exception(e)
            )

            context = get_pymongo_fallback_context(user_email)

    else:
        mcp_status = (
            "MongoDB MCP is disabled in this Render deployment for stability. "
            "The app uses PyMongo fallback for the live hosted demo. "
            "The MongoDB MCP integration code is included and can be enabled with USE_MCP=true."
        )

        context = get_pymongo_fallback_context(user_email)

    prompt = f"""
You are FinShield AI's Threat Intelligence Agent.

You are analyzing scam detection history for this Gmail user:

USER:
{user_email}

DATA SOURCE:
{context["source"]}

MCP STATUS:
{mcp_status}

RECENT SCAMS:
{_json_safe(context["recent_scams"])}

CATEGORY SUMMARY:
{_json_safe(context["category_summary"])}

HIGH RISK EMAILS:
{_json_safe(context["high_risk"])}

Create a concise threat intelligence report.

Return clean Markdown with these sections:

## 1. Overall threat status
## 2. Most common scam patterns
## 3. Highest risk threats
## 4. Recommended user actions
## 5. MongoDB MCP integration note

Keep it clear, impressive, and dashboard-friendly.
"""

    response = model.generate_content(prompt)

    return response.text.strip()


if __name__ == "__main__":
    print(test_mcp_connection())