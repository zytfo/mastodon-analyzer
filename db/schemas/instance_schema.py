from datetime import datetime
from typing import Dict

from pydantic import BaseModel


class InstanceSchema(BaseModel):
    id: str
    name: str | None = None
    added_at: datetime | None = None
    updated_at: datetime | None = None
    checked_at: datetime | None = None
    uptime: int | None = 0
    up: bool | None = False
    dead: bool | None = False
    version: str | None = None
    ipv6: bool | None = False
    https_score: int | None = None
    https_rank: str | None = None
    obs_score: int | None = None
    obs_rank: str | None = None
    users: str | None = None
    statuses: str | None = None
    connections: str | None = None
    open_registrations: bool | None = False
    info: Dict | None = {}
    thumbnail: str | None = None
    thumbnail_proxy: str | None = None
    active_users: int | None = 0
    email: str | None = None
    admin: str | None = None
