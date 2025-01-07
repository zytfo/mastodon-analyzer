from sqlalchemy.orm import Mapped

from db.db_setup import Base
from db.models.base import big_int_pk, big_int_pk_increment


class TrendModel(Base):
    __tablename__ = "trends"

    id: Mapped[big_int_pk]
    name: Mapped[str]
    url: Mapped[str]
    uses_in_last_seven_days: Mapped[int]


class SuspiciousTrendModel(Base):
    __tablename__ = "suspicious_trends"

    id: Mapped[big_int_pk_increment]
    name: Mapped[str]
    url: Mapped[str]
    uses_in_last_seven_days: Mapped[int]
    number_of_accounts: Mapped[int]
    instance_url: Mapped[str]
    number_of_similar_statuses: Mapped[int]
