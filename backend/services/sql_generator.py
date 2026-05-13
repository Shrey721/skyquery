import logging
import json
from typing import List, Dict, Any
from app.services.prompt_loader import load_prompt
from app.services.copilot_sdk import get_copilot_chat_completion

logger = logging.getLogger(__name__)

async def generate_sql(question: str, selected_tables: List[str], conversation_history: List[Dict[str, str]], schema_json: str) -> Dict[str, Any]:
    """Generate SQL using the LLM.

    Parameters
    ----------
    question: str
        The user question.
    selected_tables: List[str]
        Tables chosen by the table selector.
    conversation_history: List[Dict[str, str]]
        Prior interactions, each with ``role`` and ``content`` keys.
    schema_json: str
        JSON string of the full schema (used for context).
    """
    logger.debug("Generating SQL for question '%s' with tables %s", question, selected_tables)
    prompt_template = load_prompt("sql_generator.txt")
    context = {
        "question": question,
        "tables": selected_tables,
        "schema": json.loads(schema_json) if schema_json else {},
        "history": conversation_history[-3:],
    }
    prompt = prompt_template.format(**context)
    model_name = "gpt-4"
    try:
        response = await get_copilot_chat_completion(github_token="", model=model_name, prompt=prompt)
        if not response.get("success"):
            raise RuntimeError(response.get("error_message", "LLM generation failed"))
        generated = json.loads(response.get("response_text", "{}"))
        logger.info("SQL generation succeeded: %s", generated)
        return generated
    except Exception as e:
        logger.exception("SQL generation error: %s", e)
        raise
