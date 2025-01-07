# stdlib
import datetime
from typing import Annotated

# thirdparty
from sqlalchemy import BigInteger, text
from sqlalchemy.orm import DeclarativeBase, mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True, unique=True, autoincrement=False)]
str_pk = Annotated[str, mapped_column(primary_key=True, unique=True)]
int_pk_increment = Annotated[int, mapped_column(primary_key=True, unique=True, autoincrement=True)]
big_int = Annotated[int, mapped_column(type_=BigInteger)]
big_int_pk = Annotated[int, mapped_column(primary_key=True, unique=True, autoincrement=False, type_=BigInteger)]
big_int_pk_increment = Annotated[
    int, mapped_column(primary_key=True, unique=True, autoincrement=True, type_=BigInteger)
]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class Base(DeclarativeBase):
    repr_cols_num: int = 3
    repr_cols: tuple = ()

    def __repr__(self) -> str:
        cols = [
            f"{col}={getattr(self, col)}"
            for idx, col in enumerate(self.__table__.columns.keys())
            if col in self.repr_cols or idx < self.repr_cols_num
        ]
        return f"<{self.__class__.__name__} {', '.join(cols)}>"
