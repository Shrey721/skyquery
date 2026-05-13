from typing import Any, Dict, List


def shape_result(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = rows or []

    columns = list(rows[0].keys()) if rows else []

    preview_rows = rows[:100]
    limited_rows = rows[:10000]

    chart_suggestion = "table"
    if len(columns) == 2 and rows:
        chart_suggestion = "bar"

    return {
        "columns": columns,
        "row_count": len(rows),
        "rows": limited_rows,
        "preview_rows": preview_rows,
        "chart_suggestion": chart_suggestion,
    }


def shape_results(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return shape_result(rows)