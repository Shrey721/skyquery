import os

# Directory to store system prompts for each LLM stage.
PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")

def load_prompt(filename: str) -> str:
    """Read a prompt file from the prompts directory.

    Args:
        filename: Name of the prompt file (e.g., "intent.txt").
    Returns:
        The prompt text.
    """
    path = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
