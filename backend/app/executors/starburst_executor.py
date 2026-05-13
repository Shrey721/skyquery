import os
import asyncio
import logging
from typing import List, Dict, Any

import trino

logger = logging.getLogger(__name__)


class StarburstExecutor:

    def __init__(self):
        self.mock_mode = (
            str(os.getenv("MOCK_EXECUTION", "false")).lower() == "true"
        )

        if self.mock_mode:
            logger.info("Running in MOCK mode")
            self.connection = None
            return

        self.connection = trino.dbapi.connect(
            host=os.getenv("TRINO_HOST", "localhost"),
            port=int(os.getenv("TRINO_PORT", 8080)),
            user=os.getenv("TRINO_USER", "admin"),
            catalog=os.getenv("TRINO_CATALOG", "aviation"),
            schema=os.getenv("TRINO_SCHEMA", "public"),
        )

        logger.info("Connected to Trino successfully")

    async def execute(self, sql: str) -> List[Dict[str, Any]]:

        # Clean SQL before sending to Trino
        sql = sql.strip().rstrip(";").strip()

        logger.info("Executing cleaned SQL: %s", sql)
        print("EXECUTING CLEANED SQL:", sql)

        if self.mock_mode:
            await asyncio.sleep(0.1)

            return [
                {
                    "delayed_flights": 342,
                    "mock": True
                }
            ]

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            results = [
                dict(zip(columns, row))
                for row in rows
            ]

            logger.info("Returned %s rows", len(results))
            return results

        except Exception as e:
            logger.exception("Trino execution failed")
            raise RuntimeError(str(e))