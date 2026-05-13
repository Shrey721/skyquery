import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def classify_intent(
    question: str,
    schema: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Lightweight intent classifier.
    Schema is optional for compatibility with pipeline calls.
    """

    q = question.lower()

    if any(word in q for word in ["trend", "over time", "daily", "weekly", "monthly"]):
        intent = "time_series"

    elif any(word in q for word in ["compare", "vs", "versus"]):
        intent = "comparison"

    elif any(word in q for word in ["schema", "columns", "tables", "available"]):
        intent = "schema_exploration"

    elif any(word in q for word in ["same", "instead", "exclude", "break it down"]):
        intent = "follow_up_refinement"

    elif any(word in q for word in ["search", "contains", "keyword"]):
        intent = "free_text_search"

    else:
        intent = "aggregation"

    logger.info("Intent classified as %s", intent)

    return {
        "intent": intent,
        "reason": "Keyword-based classification."
    }