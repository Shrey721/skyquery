from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import logging
import asyncio

from backend.pipeline.nl_sql_pipeline import NLtoSQLPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    session_id: str | None = None

class QueryResponse(BaseModel):
    intent: str
    selected_tables: list
    generated_sql: str
    validation: Dict[str, Any]
    results: Dict[str, Any]
    summary: str
    execution_time_ms: int

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        pipeline = NLtoSQLPipeline()
        response = await pipeline.process(request.question, request.session_id)
        return response
    except Exception as e:
        logger.exception("Error in /query endpoint: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
