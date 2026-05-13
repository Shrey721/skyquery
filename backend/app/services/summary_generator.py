import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


async def generate_summary(
    question: str,
    sql: str | None = None,
    result: Any = None,
    schema: Dict[str, Any] | None = None,
    history: list | None = None,
    recent_sqls: list | None = None,
    result_preview: list | None = None,
    **kwargs
) -> str:

    result = result if result is not None else kwargs.get("shaped_result")

    if isinstance(result, list):
        row_count = len(result)
        preview_rows = result[:5]

    elif isinstance(result, dict):
        row_count = result.get("row_count", 0)
        preview_rows = result_preview or result.get("preview_rows", [])

    else:
        row_count = 0
        preview_rows = []

    if preview_rows:
        return f"The query ran successfully and returned {row_count} row(s) for: {question}"

    return f"The query ran successfully but returned {row_count} row(s)."