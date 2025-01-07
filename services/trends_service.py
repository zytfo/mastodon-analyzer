from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_setup import ScopedSession
from db.models.trend_model import SuspiciousTrendModel, TrendModel


async def delete_all_trends(session: AsyncSession):
    query = delete(TrendModel)
    await session.execute(query)


async def update_and_retrieve_trends(session: AsyncSession, trends: list):
    session.add_all(trends)

    query = select(TrendModel)
    result = await session.execute(query)
    return result.scalars().all()


def check_if_trend_exist(session: ScopedSession, name: str):
    query = select(TrendModel).filter(TrendModel.name == name)  # noqa
    result = session.execute(query)
    return result.scalars().one_or_none()


def check_if_suspicious_trend_exist(session: ScopedSession, name: str):
    query = select(SuspiciousTrendModel).filter(SuspiciousTrendModel.name == name)  # noqa
    result = session.execute(query)
    return result.scalars().one_or_none()


def create_or_update_suspicious_trend(
    session: ScopedSession,
    name: str,
    url: str,
    uses_in_last_seven_days: int,
    number_of_accounts: int,
    instance_url: str,
):
    insert_stmt = (
        insert(SuspiciousTrendModel)
        .values(
            dict(
                name=name,
                url=url,
                uses_in_last_seven_days=uses_in_last_seven_days,
                number_of_accounts=number_of_accounts,
                instance_url=instance_url,
            )
        )
        .returning(SuspiciousTrendModel)
    )

    insert_stmt = insert_stmt.on_conflict_do_update(  # noqa
        index_elements=["url"],
        set_=dict(uses_in_last_seven_days=uses_in_last_seven_days, number_of_accounts=number_of_accounts),
    )

    result = session.execute(insert_stmt)
    result = result.fetchone()

    return result


def increment_suspicious_trend_number_of_similar_posts(
    session: ScopedSession, suspicious_trend_id: int, number_of_similar_statuses: int
):
    query = (
        update(SuspiciousTrendModel)
        .values(dict(number_of_similar_statuses=number_of_similar_statuses))
        .filter(SuspiciousTrendModel.id == suspicious_trend_id)  # noqa
    )

    session.execute(query)
