from datetime import datetime

from pydantic import BaseModel


class AccountSchema(BaseModel):
    id: int
    username: str | None = ""
    acct: str | None = ""
    display_name: str | None = ""
    locked: bool | None = False
    bot: bool | None = False
    discoverable: bool | None = False
    group: bool | None = False
    created_at: datetime | None = None
    note: str | None = None
    url: str | None = None
    avatar: str | None = None
    avatar_static: str | None = None
    header: str | None = None
    header_static: str | None = None
    followers_count: int | None = 0
    following_count: int | None = 0
    statuses_count: int | None = 0
    last_status_at: datetime | None = None
    instance_url: str | None = None
