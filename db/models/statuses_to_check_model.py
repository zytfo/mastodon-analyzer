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
    chatgpt_response: Mapped[str]
    checked_at: Mapped[datetime]
    author_followers_count: Mapped[int]
    author_following_count: Mapped[int]
    author_statuses_count: Mapped[int]
    author_created_at: Mapped[datetime]
