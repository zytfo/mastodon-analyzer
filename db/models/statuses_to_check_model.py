from datetime import datetime

from sqlalchemy.orm import Mapped

from db.db_setup import Base
from db.models.base import created_at, str_pk


class StatusToCheckModel(Base):
    __tablename__ = "statuses_to_check"

    id: Mapped[str_pk]
    created_at: Mapped[created_at]
    language: Mapped[str]
    url: Mapped[str]
    content: Mapped[str]
    is_suspicious: Mapped[bool]
    openai_response: Mapped[str | None]
    openai_confidence: Mapped[float | None]
    openai_is_suspicious: Mapped[bool | None]
    claude_response: Mapped[str | None]
    claude_confidence: Mapped[float | None]
    claude_is_suspicious: Mapped[bool | None]
    llama_response: Mapped[str | None]
    llama_confidence: Mapped[float | None]
    llama_is_suspicious: Mapped[bool | None]
    gemini_response: Mapped[str | None]
    gemini_confidence: Mapped[float | None]
    gemini_is_suspicious: Mapped[bool | None]
    checked_at: Mapped[datetime]
    author_followers_count: Mapped[int]
    author_following_count: Mapped[int]
    author_statuses_count: Mapped[int]
    author_created_at: Mapped[datetime]
