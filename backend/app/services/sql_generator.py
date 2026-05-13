import os
import logging
import json
import re
import ast
from typing import Dict, Any, List

from app.services.prompt_loader import load_prompt
from app.services.copilot_sdk import get_copilot_chat_completion

logger = logging.getLogger(__name__)


def _safe_json_loads(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return {}

    return {}


def _ensure_list(value: Any) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        return [value]

    return []


def _extract_table_name(selected_tables: Any) -> str:
    if not selected_tables:
        return "flight_ops"

    first = selected_tables[0]

    if isinstance(first, dict):
        return (
            first.get("table")
            or first.get("name")
            or first.get("table_name")
            or "flight_ops"
        )

    return str(first)


def _extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """
    Copilot SDK may return either:
    1. raw JSON string
    2. SessionEvent(... content='JSON HERE' ...)
    This extracts the JSON safely.
    """

    if not response_text:
        raise ValueError("Empty LLM response text")

    # Case 1: direct JSON
    try:
        return json.loads(response_text)
    except Exception:
        pass

    # Case 2: SessionEvent wrapper with content='...'
    match = re.search(r"content='(.*?)', message_id=", response_text, re.DOTALL)
    if match:
        content_literal = "'" + match.group(1) + "'"

        try:
            content = ast.literal_eval(content_literal)
            return json.loads(content)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON from SessionEvent content: {e}")

    # Case 3: fallback extract first JSON object
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError("Could not extract JSON from LLM response")


async def generate_sql(
    question: str,
    selected_tables: List[Any] | None = None,
    conversation_history: List[Dict[str, str]] | None = None,
    schema_json: str | Dict[str, Any] | None = None,
    schema: Dict[str, Any] | None = None,
    intent: Dict[str, Any] | None = None,
    recent_sqls: list | None = None,
    history: list | None = None,
    sample_values: dict | None = None,
    copilot_token: str | None = None,
    **kwargs
) -> Dict[str, Any]:

    selected_tables = _ensure_list(selected_tables or kwargs.get("tables"))
    conversation_history = _ensure_list(conversation_history or history)
    recent_sqls = _ensure_list(recent_sqls)

    schema_context = schema or _safe_json_loads(schema_json)
    table_name = _extract_table_name(selected_tables)

    print("\n========== SQL GENERATOR DEBUG ==========")
    print("QUESTION:", question)
    print("SELECTED TABLES:", selected_tables)
    print("TABLE NAME USED:", table_name)
    print("SCHEMA TYPE:", type(schema_context))
    print("SCHEMA PREVIEW:", str(schema_context)[:500])
    print("RECENT SQLS:", recent_sqls[-3:])

    try:
        prompt_template = load_prompt("sql_generator.txt")

        context = {
            "question": question,
            "tables": selected_tables,
            "selected_tables": selected_tables,
            "schema": schema_context,
            "history": conversation_history[-3:],
            "recent_sqls": recent_sqls[-3:],
            "sample_values": sample_values or {},
            "intent": intent or {},
        }

        prompt = prompt_template.format(**context)

        print("\n----- PROMPT SENT TO COPILOT -----")
        print(prompt[:3000])
        print("----- END PROMPT PREVIEW -----\n")

        resolved_token = (
            copilot_token
            or kwargs.get("github_token")
            or os.getenv("GITHUB_COPILOT_TOKEN", "")
        )

        print("SQL GENERATOR RECEIVED TOKEN:", bool(copilot_token))
        print("ENV TOKEN EXISTS:", bool(os.getenv("GITHUB_COPILOT_TOKEN", "")))
        print("FINAL TOKEN EXISTS:", bool(resolved_token))

        response = await get_copilot_chat_completion(
            github_token=resolved_token,
            model="gpt-4.1",
            prompt=prompt
        )

        print("----- RAW COPILOT SDK RESPONSE -----")
        print(response)
        print("----- END RAW RESPONSE -----")

        if not response.get("success"):
            raise RuntimeError(
                response.get("error_message", "LLM generation failed")
            )

        response_text = response.get("response_text", "{}")

        print("----- RAW LLM TEXT -----")
        print(response_text)
        print("----- END RAW LLM TEXT -----")

        generated = _extract_json_from_response(response_text)

        if "sql" not in generated:
            raise ValueError("LLM response JSON missing 'sql' key")

        print("✅ LLM GENERATED SQL SUCCESSFULLY")
        print("SQL:", generated["sql"])
        print("=========================================\n")

        logger.info("SQL generation succeeded: %s", generated)
        return generated

    except Exception as e:
        print("❌ USING FALLBACK SQL")
        print("FALLBACK REASON:", repr(e))
        print("=========================================\n")

        logger.warning(
            "LLM SQL generation failed, using fallback SQL. Error: %s",
            e
        )

        fallback_sql = f"""
SELECT COUNT(*) AS result_count
FROM {table_name}
LIMIT 100
""".strip()

        return {
            "assumption": "Fallback SQL was used because LLM SQL generation failed.",
            "sql": fallback_sql,
            "chart_type": "table",
            "explanation": f"Generated a safe fallback SELECT query using table {table_name}."
        }