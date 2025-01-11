from datetime import datetime

from pydantic import BaseModel


class SuspiciousStatusSchema(BaseModel):
    id: str
    created_at: datetime
    language: str | None = ""
    url: str | None = ""
    content: str | None = ""
    is_suspicious: bool | None = None
    chatgpt_response: str | None = None
    checked_at: datetime | None = None
    author_followers_count: int | None = 0
    author_following_count: int | None = 0
    author_statuses_count: int | None = 0
    author_created_at: datetime | None = None
