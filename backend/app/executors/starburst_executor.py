import os
import asyncio
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class StarburstExecutor:
    def __init__(self, connection: Optional[Any] = None):
        self.connection = connection

        mock_value = os.getenv("MOCK_EXECUTION", "false")
        self.mock_mode = True

        print("MOCK_EXECUTION VALUE:", mock_value)
        print("MOCK MODE:", self.mock_mode)

        if self.mock_mode:
            logger.info("StarburstExecutor running in MOCK mode.")

    async def execute(self, sql: str) -> List[Dict[str, Any]]:
        logger.debug("Executing SQL: %s", sql)

        if self.mock_mode:
            await asyncio.sleep(0.1)
            return [
                {
                    "delayed_flights": 342,
                    "mock": True
                }
            ]

        if not self.connection:
            raise RuntimeError(
                "No Trino connection available for execution. "
                "Set MOCK_EXECUTION=true before starting uvicorn."
            )

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.exception("SQL execution error: %s", e)
            raise RuntimeError(str(e))