from typing import Any, Dict
import re

FORBIDDEN = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]


async def validate_sql(sql: str, schema: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if not sql or not isinstance(sql, str):
        return {"valid": False, "is_valid": False, "errors": ["SQL is empty"]}

    cleaned = sql.strip()
    upper = cleaned.upper()

    if not upper.startswith("SELECT"):
        return {"valid": False, "is_valid": False, "errors": ["Only SELECT queries are allowed"]}

    for word in FORBIDDEN:
        if re.search(rf"\b{word}\b", upper):
            return {"valid": False, "is_valid": False, "errors": [f"Forbidden SQL keyword used: {word}"]}

    if cleaned.count(";") > 1:
        return {"valid": False, "is_valid": False, "errors": ["Multiple SQL statements are not allowed"]}

    return {"valid": True, "is_valid": True, "errors": []}