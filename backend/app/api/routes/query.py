from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict
import logging

from app.pipeline.nl_sql_pipeline import NLtoSQLPipeline
from app.api.routes.auth import redis_client

logger = logging.getLogger(__name__)

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    session_id: str | None = None


@router.post("/query", response_model=Dict[str, Any])
async def query_endpoint(request: QueryRequest, req: Request):
    try:
        session_id = request.session_id or req.session.get("session_id") or "demo"
        token_key = f"copilot_token:{session_id}"
        raw_token = redis_client.get(token_key)

        print("QUERY SESSION ID:", session_id)
        print("QUERY TOKEN KEY:", token_key)
        print("QUERY REDIS CLIENT:", redis_client)
        print("QUERY RAW TOKEN EXISTS:", bool(raw_token))

        if not raw_token:
            raise HTTPException(
                status_code=401,
                detail="Copilot authentication required for this session"
            )

        copilot_token = (
            raw_token.decode("utf-8")
            if isinstance(raw_token, bytes)
            else str(raw_token)
        )

        print("QUERY ROUTE TOKEN EXISTS:", bool(copilot_token))

        pipeline = NLtoSQLPipeline()

        result = await pipeline.process(
            question=request.question,
            session_id=session_id,
            copilot_token=copilot_token,
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("NL-to-SQL pipeline failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))