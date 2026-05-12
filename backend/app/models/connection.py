from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# --- SQLAlchemy DB Models ---

class ConnectionRecord(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    catalog = Column(String, nullable=False)
    schema_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=True)
    ssl_enabled = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)

# --- Pydantic Models for API ---

class TrinoConnectionRequest(BaseModel):
    host: str = Field(..., description="Trino coordinator hostname")
    port: int = Field(8080, description="Trino coordinator port")
    catalog: str = Field(..., description="Target catalog name")
    schema_name: str = Field(..., alias="schema", description="Target schema name")
    username: str = Field(..., description="Trino username")
    password: Optional[str] = Field(None, description="Trino password or token")
    ssl_enabled: bool = Field(False, alias="ssl", description="Use SSL for connection")

    class Config:
        populate_by_name = True


class TrinoConnectionResponse(BaseModel):
    id: Optional[int] = None
    host: str
    port: int
    catalog: str
    schema_name: str
    username: str
    ssl_enabled: bool
    is_active: bool

    class Config:
        from_attributes = True
