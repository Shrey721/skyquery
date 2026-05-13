import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def select_tables(
    question: str,
    schema: Dict[str, Any],
    intent: Dict[str, Any] | None = None
) -> List[Dict[str, Any]]:
    """
    Select top relevant tables from schema metadata.
    MVP version uses keyword overlap.
    """
    q = question.lower()
    tables = schema.get("tables", schema)

    selected = []

    for table_name, table_meta in tables.items():
        columns = table_meta.get("columns", [])
        if isinstance(columns, dict):
            columns = list(columns.keys())

        score = 0.0
        reasons = []

        if table_name.lower() in q:
            score += 0.5
            reasons.append("table name matched question")

        for col in columns:
            col_l = str(col).lower()
            if col_l in q:
                score += 0.2
                reasons.append(f"column matched: {col}")

        # Aviation-specific fallback hints
        if any(w in q for w in ["flight", "flights", "delayed", "carrier", "atl", "airport"]):
            if "flight" in table_name.lower() or "ops" in table_name.lower():
                score += 0.4
                reasons.append("flight-related query matched flight table")

        if any(w in q for w in ["weather", "storm", "rain", "wind"]):
            if "weather" in table_name.lower():
                score += 0.4
                reasons.append("weather-related query matched weather table")

        if any(w in q for w in ["radar", "altitude", "squawk", "track"]):
            if "radar" in table_name.lower() or "track" in table_name.lower():
                score += 0.4
                reasons.append("radar-related query matched radar table")

        if score > 0:
            selected.append({
                "table": table_name,
                "score": round(min(score, 1.0), 2),
                "reason": "; ".join(reasons) or "keyword match"
            })

    selected = sorted(selected, key=lambda x: x["score"], reverse=True)[:3]

    if not selected and tables:
        first_table = list(tables.keys())[0]
        selected = [{
            "table": first_table,
            "score": 0.1,
            "reason": "fallback: no strong table match found"
        }]

    logger.info("Selected tables: %s", selected)
    return selected