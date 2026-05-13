import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def repair_sql(
    question: str,
    failed_sql: str,
    error_message: str,
    schema: Dict[str, Any] | None = None,
    recent_sqls: list | None = None,
    history: list | None = None,
    selected_tables: list | None = None,
    intent: Dict[str, Any] | None = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Simple fallback SQL repair service.
    Later replace with real LLM repair logic.
    """

    logger.warning(
        "Repairing SQL. Error: %s | Failed SQL: %s",
        error_message,
        failed_sql,
    )

    repaired_sql = failed_sql.strip()

    # Remove dangerous statements if present
    forbidden = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE",
        "CREATE"
    ]

    upper_sql = repaired_sql.upper()

    for keyword in forbidden:
        if keyword in upper_sql:
            repaired_sql = "SELECT 1 AS blocked_query"
            break

    # Ensure SELECT
    if not repaired_sql.upper().startswith("SELECT"):
        repaired_sql = "SELECT 1 AS repaired_query"

    # Ensure LIMIT
    if "LIMIT" not in repaired_sql.upper():
        repaired_sql += "\nLIMIT 100"

    logger.info("Repaired SQL: %s", repaired_sql)

    return {
        "sql": repaired_sql,
        "repair_explanation": "Applied fallback SQL repair logic."
    }