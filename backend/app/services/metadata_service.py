import json
from sqlalchemy.orm import Session
from app.services import connection_store, trino_service
from app.models.connection import TrinoConnectionRequest
from app.models.metadata import SchemaMetadata, TableMetadata, ColumnMetadata
from app.services import redis_cache

def discover_and_cache_metadata(db: Session) -> SchemaMetadata:
    """
    Connects to Trino using the active connection, queries the information_schema,
    builds the SchemaMetadata object, and caches it in Redis.
    """
    active_conn = connection_store.get_active_connection(db)
    if not active_conn:
        raise ValueError("No active Trino connection found.")

    conn_req = TrinoConnectionRequest(
        host=active_conn.host,
        port=active_conn.port,
        catalog=active_conn.catalog,
        schema=active_conn.schema_name,
        username=active_conn.username,
        password=connection_store.decrypt_password(active_conn.encrypted_password),
        ssl=active_conn.ssl_enabled
    )

    try:
        conn = trino_service.get_trino_connection(conn_req)
        cur = conn.cursor()

        # 1. Fetch tables
        cur.execute(f"SELECT table_catalog, table_schema, table_name FROM information_schema.tables WHERE table_schema = '{active_conn.schema_name}' AND table_catalog = '{active_conn.catalog}'")
        tables_rows = cur.fetchall()

        table_dict = {}
        for row in tables_rows:
            cat, schema, table = row
            table_dict[table] = TableMetadata(
                catalog=cat,
                schema_name=schema,
                table_name=table,
                columns=[],
                row_count=None
            )

        # 2. Fetch columns
        cur.execute(f"SELECT table_name, column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = '{active_conn.schema_name}' AND table_catalog = '{active_conn.catalog}'")
        columns_rows = cur.fetchall()

        for row in columns_rows:
            table, col, dtype, nullable = row
            if table in table_dict:
                table_dict[table].columns.append(ColumnMetadata(
                    name=col,
                    data_type=dtype,
                    is_nullable=(nullable == 'YES')
                ))

        # 3. Fetch stats (row count)
        for table in table_dict.keys():
            try:
                cur.execute(f"SHOW STATS FOR {active_conn.catalog}.{active_conn.schema_name}.{table}")
                stats_rows = cur.fetchall()
                # Typically, SHOW STATS returns rows where the last row (where column_name is NULL) contains table-level stats.
                # Or we can just look for the row where column_name is None/NULL
                for row in stats_rows:
                    # In Trino, SHOW STATS returns: column_name, data_size, distinct_values_count, nulls_fraction, row_count, low_value, high_value
                    # Usually, the row with column_name IS NULL has the table row_count.
                    if row[0] is None:
                        # row_count is the 5th column (index 4) typically.
                        if len(row) > 4 and row[4] is not None:
                            table_dict[table].row_count = int(row[4])
                        break
            except Exception as e:
                # If SHOW STATS fails for some reason (e.g. view), just ignore and leave row_count as None
                print(f"Failed to fetch stats for {table}: {e}")

        # Build schema metadata
        schema_metadata = SchemaMetadata(tables=list(table_dict.values()))

        # Cache in Redis
        redis_cache.set_metadata(schema_metadata.model_dump_json())

        return schema_metadata

    except Exception as e:
        raise Exception(f"Failed to discover metadata: {str(e)}")

def get_cached_metadata() -> SchemaMetadata:
    """
    Retrieves metadata from Redis.
    """
    cached_json = redis_cache.get_metadata()
    if cached_json:
        return SchemaMetadata.model_validate_json(cached_json)
    return None
