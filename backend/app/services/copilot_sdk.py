import os

MOCK_MODE = str(os.getenv("MOCK_EXECUTION", "false")).lower() == "true"

try:
    if not MOCK_MODE:
        from copilot import CopilotClient, SubprocessConfig
    else:
        CopilotClient = None
        SubprocessConfig = None
except ImportError:
    CopilotClient = None
    SubprocessConfig = None

async def approve_permission(*args, **kwargs):
    return {"approve": True}

async def get_copilot_chat_completion(
    github_token: str,
    model: str,
    prompt: str,
) -> dict:
    if CopilotClient is None or SubprocessConfig is None:
        return {
            "success": False,
            "response_text": None,
            "error_message": "Copilot SDK not installed or import failed",
        }

    client = None

    try:
        print("[Copilot SDK] Starting SDK request")

        config = SubprocessConfig(
            github_token=github_token,
            use_logged_in_user=False,
        )

        client = CopilotClient(config=config)

        await client.start()
        print("[Copilot SDK] Client started")

        session = await client.create_session(
            on_permission_request=approve_permission,
            model=model,
            session_id="skyquery-test-session",
        )

        print("[Copilot SDK] Session created")

        response = await session.send_and_wait(prompt)

        print("[Copilot SDK] Prompt sent successfully")

        if isinstance(response, dict):
            content = (
                response.get("content")
                or response.get("text")
                or response.get("response")
                or str(response)
            )
        else:
            content = (
                getattr(response, "content", None)
                or getattr(response, "text", None)
                or getattr(response, "message", None)
                or str(response)
            )

        return {
            "success": True,
            "response_text": content,
            "error_message": None,
        }

    except Exception as e:
        print(f"[Copilot SDK] Error: {str(e)}")
        return {
            "success": False,
            "response_text": None,
            "error_message": str(e),
        }

    finally:
        if client is not None:
            try:
                await client.stop()
            except Exception:
                pass