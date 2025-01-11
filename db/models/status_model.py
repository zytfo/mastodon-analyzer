from datetime import datetime

from sqlalchemy.orm import Mapped

from db.db_setup import Base
from db.models.base import big_int, created_at, str_pk


class StatusModel(Base):
    __tablename__ = "statuses"

    id: Mapped[str_pk]
    created_at: Mapped[created_at]
    in_reply_to_id: Mapped[big_int]
    in_reply_to_account_id: Mapped[big_int]
    sensitive: Mapped[bool]
    spoiler_text: Mapped[str]
    visibility: Mapped[str]
    language: Mapped[str]
    uri: Mapped[str]
    url: Mapped[str]
    replies_count: Mapped[int]
    reblogs_count: Mapped[int]
    favourites_count: Mapped[int]
    edited_at: Mapped[datetime]
    content: Mapped[str]
    tags: Mapped[str]


class RawStatusModel(Base):
    __tablename__ = "raw_statuses"

    id: Mapped[str_pk]
    created_at: Mapped[created_at]
    in_reply_to_id: Mapped[big_int]
    in_reply_to_account_id: Mapped[big_int]
    sensitive: Mapped[bool]
    spoiler_text: Mapped[str]
    visibility: Mapped[str]
    language: Mapped[str]
    uri: Mapped[str]
    url: Mapped[str]
    replies_count: Mapped[int]
    reblogs_count: Mapped[int]
    favourites_count: Mapped[int]
    edited_at: Mapped[datetime]
    content: Mapped[str]
    tags: Mapped[str]
