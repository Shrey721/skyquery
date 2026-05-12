from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.models.connection import Base
from pydantic import BaseModel
from typing import Optional

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserResponse(BaseModel):
    id: int
    github_id: str
    username: str
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        from_attributes = True
