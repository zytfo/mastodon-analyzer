from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.db_setup import Base
from db.models.base import created_at, str_pk


class InstanceModel(Base):
    __tablename__ = "instances"

    id: Mapped[str_pk]
    name: Mapped[str]
    added_at: Mapped[created_at]
    updated_at: Mapped[datetime]
    checked_at: Mapped[datetime]
    uptime: Mapped[int]
    up: Mapped[bool]
    dead: Mapped[bool]
    version: Mapped[str]
    ipv6: Mapped[bool]
    https_score: Mapped[int]
    https_rank: Mapped[str]
    obs_score: Mapped[int]
    obs_rank: Mapped[str]
    users: Mapped[str]
    statuses: Mapped[str]
    connections: Mapped[str]
    open_registrations: Mapped[bool]
    info: Mapped[dict] = mapped_column(JSONB)
    thumbnail: Mapped[str]
    thumbnail_proxy: Mapped[str]
    active_users: Mapped[int]
    email: Mapped[str]
    admin: Mapped[str]
