import logging
from typing import List, Dict, Any
from app.services.redis_cache import get_metadata

logger = logging.getLogger(__name__)

def select_tables(question: str, schema_json: str, top_n: int = 3) -> Dict[str, Any]:
    """Select the most relevant tables for a user question.

    A simple keyword‑matching approach is used: we split the question into
    lowercase words and count occurrences of each table name in the schema.
    The schema is expected to be a JSON string representing a mapping of
    table names to a list of column names, e.g.:

    ```json
    {"flights": ["flight_id", "origin", "dest", "delay"], "airports": [...]}
    ```

    The function returns a JSON‑serialisable dict containing the selected
    tables and a relevance score.
    """
    logger.debug("Selecting tables for question: %s", question)
    if not schema_json:
        logger.warning("No schema metadata available in Redis.")
        return {"selected_tables": [], "relevance": {}}

    try:
        import json
        schema = json.loads(schema_json)
    except Exception as e:
        logger.exception("Failed to parse schema JSON: %s", e)
        return {"selected_tables": [], "relevance": {}}

    tokens = [t.strip(".,!?;:") for t in question.lower().split()]
    scores: Dict[str, int] = {}
    for table in schema.keys():
        score = sum(1 for token in tokens if token in table.lower())
        # also boost score if any column matches
        columns = schema.get(table, [])
        score += sum(1 for token in tokens if any(token in col.lower() for col in columns))
        if score > 0:
            scores[table] = score

    # Sort tables by descending score and take top_n
    selected = sorted(scores, key=scores.get, reverse=True)[:top_n]
    relevance = {tbl: scores[tbl] for tbl in selected}
    logger.info("Selected tables: %s with relevance %s", selected, relevance)
    return {"selected_tables": selected, "relevance": relevance}
