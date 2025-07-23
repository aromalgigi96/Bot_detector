# app/models.py
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """Registered users."""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False, unique=True)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LoginAttempt(SQLModel, table=True):
    """Every login (bot or human)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    username: str = Field(nullable=False)
    ip: str = Field(nullable=False)
    uri: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    time_to_submit: float = Field(nullable=False)
    label: str = Field(nullable=False)    # "Benign" or "Attack"
    score: float = Field(nullable=False)   # e.g. 0.01 or 0.99