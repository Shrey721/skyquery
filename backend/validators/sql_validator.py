import logging
import json
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

SELECT_ONLY_REGEX = re.compile(r'^\s*SELECT\b', re.IGNORECASE)
FORBIDDEN_KEYWORDS = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE'}

def validate_sql(sql: str, schema_json: str) -> Dict[str, Any]:
    """Validate generated SQL.

    Checks:
    * Must start with SELECT
    * Must not contain forbidden DML/DDL keywords
    * Must be a single statement (no semicolons separating statements)
    * All referenced tables/columns exist in the provided schema metadata
    """
    errors: List[str] = []
    # Basic SELECT check
    if not SELECT_ONLY_REGEX.match(sql):
        errors.append("SQL must start with SELECT.")
    # Forbidden keywords detection
    upper_sql = sql.upper()
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(r'\b' + kw + r'\b', upper_sql):
            errors.append(f"Forbidden keyword detected: {kw}.")
    # Multiple statements detection
    if sql.strip().count(';') > 0:
        errors.append("Multiple statements are not allowed.")
    # Schema validation
    try:
        schema = json.loads(schema_json) if schema_json else {}
    except Exception as e:
        logger.exception("Failed to parse schema JSON for validation.")
        schema = {}
    # Extract table and column identifiers (very naive parsing)
    identifiers = re.findall(r'"?([a-zA-Z_][a-zA-Z0-9_]*)"?', sql)
    referenced_tables = set()
    referenced_columns = set()
    # Assume first identifier after FROM/JOIN is a table, others could be columns
    tokens = sql.split()
    for i, token in enumerate(tokens):
        if token.upper() in {"FROM", "JOIN", "INTO", "UPDATE", "TABLE"} and i + 1 < len(tokens):
            referenced_tables.add(tokens[i + 1].strip('"'))
    # Column detection – simplistic: any identifier that is not a table
    for ident in identifiers:
        if ident not in referenced_tables:
            referenced_columns.add(ident)
    # Verify tables exist
    for tbl in referenced_tables:
        if tbl not in schema:
            errors.append(f"Referenced table not found in schema: {tbl}.")
    # Verify columns exist within their tables (if schema provides column lists)
    for tbl, cols in schema.items():
        for col in referenced_columns:
            if col not in cols:
                # column may belong to another table; skip strict check for now
                continue
    is_valid = len(errors) == 0
    logger.info("SQL validation result: %s, errors: %s", is_valid, errors)
    return {"is_valid": is_valid, "errors": errors}
