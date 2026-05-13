import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
import uuid

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User, UserResponse
from app.services.redis_cache import redis_client

router = APIRouter()

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API_URL = "https://api.github.com/user"
GITHUB_EMAILS_API_URL = "https://api.github.com/user/emails"
COPILOT_COMPLETIONS_URL = "https://api.githubcopilot.com/chat/completions"

class CopilotTestRequest(BaseModel):
    prompt: str
    model: Optional[str] = None

@router.get("/github/login")
def login_via_github():
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub Client ID not configured")
    
    url = f"{GITHUB_AUTHORIZE_URL}?client_id={settings.GITHUB_CLIENT_ID}&scope=user:email"
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(request: Request, code: str, db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail="No code provided")
    
    async with httpx.AsyncClient() as client:
        # Get access token
        token_response = await client.post(
            GITHUB_ACCESS_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            }
        )
        token_data = token_response.json()
        print(f"[Auth Callback] Token response status: {token_response.status_code}")
        access_token = token_data.get("access_token")
        print(f"[Auth Callback] GitHub token prefix: {access_token[:4]}")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")
        
        # Get user info
        user_response = await client.get(
            GITHUB_USER_API_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        )
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info from GitHub")
            
        user_info = user_response.json()
        print(f"[Auth Callback] GitHub user info retrieved for: {user_info.get('login')}")
        
        # Get user email
        email = user_info.get("email")
        if not email:
            email_response = await client.get(
                GITHUB_EMAILS_API_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                primary_emails = [e for e in emails if e.get("primary") and e.get("verified")]
                if primary_emails:
                    email = primary_emails[0].get("email")
                elif emails:
                    email = emails[0].get("email")
        
        github_id = str(user_info.get("id"))
        username = user_info.get("login")
        avatar_url = user_info.get("avatar_url")
        
        # Check if user exists
        user = db.query(User).filter(User.github_id == github_id).first()
        if user:
            user.last_login = datetime.now(timezone.utc)
            user.username = username
            user.avatar_url = avatar_url
            if email:
                user.email = email
            db.commit()
            db.refresh(user)
        else:
            user = User(
                github_id=github_id,
                username=username,
                avatar_url=avatar_url,
                email=email
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        # Set session
        session_id = str(uuid.uuid4())
        request.session["user_id"] = user.id
        request.session["session_id"] = session_id
        
        # Store token securely server-side in Redis tied to this session
        # Store token securely server-side in Redis tied to this session using the required key format
        redis_client.setex(f"copilot_token:{session_id}", 86400 * 7, access_token)
        
        # Redirect to frontend
        print(f"[Auth Callback] Creating session for user {user.username} and redirecting to {settings.FRONTEND_URL}/")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/")

@router.get("/me", response_model=UserResponse)
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user

@router.post("/logout")
def logout(request: Request):
    session_id = request.session.get("session_id")
    if session_id:
        redis_client.delete(f"copilot_token:{session_id}")
    request.session.clear()
    return {"message": "Logged out successfully"}

@router.get("/token-status")
async def get_token_status(request: Request):
    user_id = request.session.get("user_id")
    session_id = request.session.get("session_id")
    
    if not user_id or not session_id:
        return {"authenticated": False, "token_exists": False, "github_api_success": False}
        
    token = redis_client.get(f"copilot_token:{session_id}")
    if not token:
        return {"authenticated": True, "token_exists": False, "github_api_success": False}
        
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            GITHUB_USER_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
        )
        api_works = user_response.status_code == 200
        
    return {
        "authenticated": True, 
        "token_exists": True, 
        "github_api_success": api_works
    }
@router.post("/copilot-llm-test")
async def test_copilot_llm(req: CopilotTestRequest, request: Request):
    # Import the SDK wrapper
    from app.services.copilot_sdk import get_copilot_chat_completion
    from app.core.config import Settings

    settings = Settings()

    user_id = request.session.get("user_id")
    session_id = request.session.get("session_id")

    if not user_id or not session_id:
        return {
            "authenticated": False,
            "github_token_exists": False,
            "copilot_sdk_ok": False,
            "safe_error_message": "Not authenticated"
        }

    github_token = redis_client.get(f"copilot_token:{session_id}")

    if not github_token:
        return {
            "authenticated": True,
            "github_token_exists": False,
            "copilot_sdk_ok": False,
            "safe_error_message": "GitHub token not found"
        }

    model_name = req.model or settings.GITHUB_COPILOT_MODEL

    try:
        # Call SDK wrapper
        result = await get_copilot_chat_completion(github_token, model_name, req.prompt)

        if not result.get("success"):
            return {
                "authenticated": True,
                "github_token_exists": True,
                "copilot_sdk_ok": False,
                "response_text": None,
                "safe_error_message": result.get("error_message"),
            }

        return {
            "authenticated": True,
            "github_token_exists": True,
            "copilot_sdk_ok": True,
            "response_text": result.get("response_text"),
            "safe_error_message": None,
        }

    except Exception as e:
        logger.error(f"Error testing copilot: {e}")
        return {
            "authenticated": True,
            "github_token_exists": True,
            "copilot_sdk_ok": False,
            "response_text": None,
            "safe_error_message": str(e),
        }

@router.get("/debug-token/{session_id}")
async def debug_token(session_id: str):
    """Return whether a Copilot token exists for the given session_id.

    The actual token value is never returned.
    """
    exists = bool(redis_client.get(f"copilot_token:{session_id}"))
    return {"session_id": session_id, "token_exists": exists}

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/debug-sessions")
async def debug_sessions():
    """List all session IDs that have a stored Copilot token.
    Returns only session IDs and a boolean flag – never the token itself.
    """
    keys = redis_client.keys("copilot_token:*")
    sessions = []
    for key in keys:
        key_str = key.decode() if isinstance(key, (bytes, bytearray)) else str(key)
        parts = key_str.split(":", 1)
        session_id = parts[1] if len(parts) > 1 else key_str
        sessions.append({"session_id": session_id, "token_exists": True})
    return {"sessions": sessions}