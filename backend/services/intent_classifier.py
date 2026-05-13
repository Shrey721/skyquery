import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def classify_intent(question: str, metadata: Dict[str, Any], history: list) -> Dict[str, Any]:
    """Classify user intent.

    A real implementation would call an LLM with a system prompt stored in
    `backend/prompts/intent.txt`. Here we return a dummy intent for illustration.
    """
    logger.debug("Classifying intent for question: %s", question)
    # Placeholder logic – in production replace with LLM call
    intent = "information_retrieval"
    return {"intent": intent, "confidence": 1.0}
