from pydantic import BaseModel


class TrendSchema(BaseModel):
    id: int
    name: str
    url: str
    uses_in_last_seven_days: int


class SuspiciousTrendSchema(BaseModel):
    id: int
    name: str
    url: str
    uses_in_last_seven_days: int
    number_of_accounts: int
    instance_url: str
    number_of_similar_statuses: int
