import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def normalize_tables(schema: Any) -> Dict[str, Any]:
    if not schema:
        return {}

    if isinstance(schema, dict):
        tables = schema.get("tables", schema)

        if isinstance(tables, dict):
            return tables

        if isinstance(tables, list):
            normalized = {}
            for table in tables:
                if not isinstance(table, dict):
                    continue

                name = (
                    table.get("name")
                    or table.get("table")
                    or table.get("table_name")
                )

                if name:
                    normalized[name] = table

            return normalized

    if isinstance(schema, list):
        normalized = {}
        for table in schema:
            if not isinstance(table, dict):
                continue

            name = (
                table.get("name")
                or table.get("table")
                or table.get("table_name")
            )

            if name:
                normalized[name] = table

        return normalized

    return {}


async def select_tables(
    question: str,
    schema: Dict[str, Any],
    intent: Dict[str, Any] | None = None,
    recent_sqls: list | None = None,
    history: list | None = None,
    **kwargs
) -> List[Dict[str, Any]]:

    tables = normalize_tables(schema)

    if not tables:
        return [{
            "table": "flight_ops",
            "score": 0.5,
            "reason": "fallback table because schema metadata was empty"
        }]

    q = question.lower()
    selected = []

    for table_name, table_meta in tables.items():
        score = 0.0
        reasons = []

        columns = table_meta.get("columns", []) if isinstance(table_meta, dict) else []

        if isinstance(columns, dict):
            columns = list(columns.keys())

        if table_name.lower() in q:
            score += 0.5
            reasons.append("table name matched")

        for col in columns:
            if isinstance(col, dict):
                col_name = (
                    col.get("name")
                    or col.get("column")
                    or col.get("column_name")
                    or ""
                )
            else:
                col_name = str(col)

            if col_name.lower() in q:
                score += 0.2
                reasons.append(f"column matched: {col_name}")

        if any(word in q for word in ["flight", "flights", "delayed", "delay", "carrier", "atl"]):
            if "flight" in table_name.lower() or "ops" in table_name.lower():
                score += 0.4
                reasons.append("flight-related query")

        if any(word in q for word in ["weather", "storm", "rain", "wind"]):
            if "weather" in table_name.lower():
                score += 0.4
                reasons.append("weather-related query")

        if any(word in q for word in ["radar", "track", "altitude", "squawk"]):
            if "radar" in table_name.lower() or "track" in table_name.lower():
                score += 0.4
                reasons.append("radar-related query")

        if score > 0:
            selected.append({
                "table": table_name,
                "score": min(round(score, 2), 1.0),
                "reason": "; ".join(reasons)
            })

    selected = sorted(selected, key=lambda x: x["score"], reverse=True)[:3]

    if not selected:
        first_table = list(tables.keys())[0]
        selected = [{
            "table": first_table,
            "score": 0.1,
            "reason": "fallback selection"
        }]

    logger.info("Selected tables: %s", selected)
    return selected