# stdlib

# thirdparty
from sqlalchemy import func, insert, select

from db.db_setup import ScopedSession
from db.models.status_model import RawStatusModel, StatusModel


def save_status(session: ScopedSession, status: dict):
    status = dict(**status)
    query = insert(StatusModel).values(status)
    session.execute(query)
    session.commit()


def save_raw_status(session: ScopedSession, status: dict):
    status = dict(**status)
    query = insert(RawStatusModel).values(status)
    session.execute(query)
    session.commit()


def get_statuses_by_tag(session: ScopedSession, tag: str):
    query = select(StatusModel).filter(func.array_to_string(StatusModel.tags, ",").ilike(func.any(["%" + tag + "%"])))
    result = session.execute(query)
    return result.scalars().all()
