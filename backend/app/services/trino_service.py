import trino
from trino.auth import BasicAuthentication
from app.models.connection import TrinoConnectionRequest


def get_trino_connection(conn_req: TrinoConnectionRequest):
    auth = None
    if conn_req.password:
        auth = BasicAuthentication(conn_req.username, conn_req.password)
    
    http_scheme = "https" if conn_req.ssl_enabled else "http"
    
    conn = trino.dbapi.connect(
        host=conn_req.host,
        port=conn_req.port,
        user=conn_req.username,
        auth=auth,
        catalog=conn_req.catalog,
        schema=conn_req.schema_name,
        http_scheme=http_scheme
    )
    return conn


def validate_connection(conn_req: TrinoConnectionRequest) -> dict:
    """
    Performs full JDBC-style connection validation against Trino.

    Steps:
        1. Verify Trino is reachable (SELECT 1)
        2. Verify catalog exists (SHOW SCHEMAS FROM <catalog>)
        3. Verify schema exists within the catalog
        4. Verify metadata can be queried (SHOW TABLES FROM <catalog>.<schema>)

    Returns a dict with:
        - success: bool
        - steps: list of {step, passed, detail} dicts
        - tables: list of table names (if all steps pass)
        - schemas: list of schema names in the catalog
        - error: str or None
    """
    steps = []
    tables = []
    schemas = []

    # Step 1: Verify Trino is reachable
    try:
        conn = get_trino_connection(conn_req)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        if result and result[0] == 1:
            steps.append({"step": "Trino Reachability", "passed": True, "detail": f"Connected to {conn_req.host}:{conn_req.port}"})
        else:
            steps.append({"step": "Trino Reachability", "passed": False, "detail": "Unexpected response from SELECT 1"})
            return {"success": False, "steps": steps, "tables": [], "schemas": [], "error": "Trino is reachable but returned unexpected result."}
    except Exception as e:
        steps.append({"step": "Trino Reachability", "passed": False, "detail": str(e)})
        return {
            "success": False,
            "steps": steps,
            "tables": [],
            "schemas": [],
            "error": f"Cannot connect to Trino at {conn_req.host}:{conn_req.port}. Is the server running? Details: {str(e)}"
        }

    # Step 2: Verify catalog exists by listing schemas
    try:
        cur.execute(f"SHOW SCHEMAS FROM {conn_req.catalog}")
        rows = cur.fetchall()
        schemas = [row[0] for row in rows]
        steps.append({
            "step": "Catalog Validation",
            "passed": True,
            "detail": f"Catalog '{conn_req.catalog}' exists with {len(schemas)} schema(s)"
        })
    except Exception as e:
        error_str = str(e)
        steps.append({"step": "Catalog Validation", "passed": False, "detail": error_str})
        return {
            "success": False,
            "steps": steps,
            "tables": [],
            "schemas": [],
            "error": f"Catalog '{conn_req.catalog}' does not exist or is not accessible. Details: {error_str}"
        }

    # Step 3: Verify schema exists within the catalog
    if conn_req.schema_name not in schemas:
        steps.append({
            "step": "Schema Validation",
            "passed": False,
            "detail": f"Schema '{conn_req.schema_name}' not found. Available: {', '.join(schemas)}"
        })
        return {
            "success": False,
            "steps": steps,
            "tables": [],
            "schemas": schemas,
            "error": f"Schema '{conn_req.schema_name}' does not exist in catalog '{conn_req.catalog}'. Available schemas: {', '.join(schemas)}"
        }
    else:
        steps.append({
            "step": "Schema Validation",
            "passed": True,
            "detail": f"Schema '{conn_req.schema_name}' exists in catalog '{conn_req.catalog}'"
        })

    # Step 4: Verify metadata can be queried (SHOW TABLES)
    try:
        cur.execute(f"SHOW TABLES FROM {conn_req.catalog}.{conn_req.schema_name}")
        rows = cur.fetchall()
        tables = [row[0] for row in rows]
        table_count = len(tables)
        steps.append({
            "step": "Metadata Query",
            "passed": True,
            "detail": f"Found {table_count} table(s) in {conn_req.catalog}.{conn_req.schema_name}"
        })
    except Exception as e:
        error_str = str(e)
        steps.append({"step": "Metadata Query", "passed": False, "detail": error_str})
        return {
            "success": False,
            "steps": steps,
            "tables": [],
            "schemas": schemas,
            "error": f"Cannot query tables in '{conn_req.catalog}.{conn_req.schema_name}'. Details: {error_str}"
        }

    return {
        "success": True,
        "steps": steps,
        "tables": tables,
        "schemas": schemas,
        "error": None
    }


def test_connection(conn_req: TrinoConnectionRequest) -> bool:
    """
    Legacy wrapper. Returns True if validation passes, raises on failure.
    """
    result = validate_connection(conn_req)
    if not result["success"]:
        raise Exception(result["error"])
    return True
