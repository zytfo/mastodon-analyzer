from datetime import datetime

from sqlalchemy.orm import Mapped

from db.db_setup import Base
from db.models.base import big_int_pk, created_at


class AccountModel(Base):
    __tablename__ = "accounts"

    id: Mapped[big_int_pk]
    username: Mapped[str]
    acct: Mapped[str]
    display_name: Mapped[str]
    locked: Mapped[bool]
    bot: Mapped[bool]
    discoverable: Mapped[bool]
    group: Mapped[bool]
    created_at: Mapped[created_at]
    note: Mapped[str]
    url: Mapped[str]
    avatar: Mapped[str]
    avatar_static: Mapped[str]
    header: Mapped[str]
    header_static: Mapped[str]
    followers_count: Mapped[int]
    following_count: Mapped[int]
    statuses_count: Mapped[int]
    last_status_at: Mapped[datetime]
    instance_url: Mapped[str]
