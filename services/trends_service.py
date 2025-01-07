import aiohttp
from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_setup import ScopedSession
from db.models.trend_model import SuspiciousTrendModel, TrendModel
from settings import get_settings
from utils.pagination import calculate_pagination

settings = get_settings()


async def delete_all_trends(session: AsyncSession):
    query = delete(TrendModel)
    await session.execute(query)


async def update_and_retrieve_trends(session: AsyncSession, trends: list):
    session.add_all(trends)

    query = select(TrendModel)
    result = await session.execute(query)
    return result.scalars().all()


async def update_mastodon_trends(session: AsyncSession):
    url = f"{settings.MASTODON_INSTANCE_ENDPOINT}/api/v1/trends/tags?limit=20"
    headers = {"Content-Type": "application/json"}
    async with aiohttp.ClientSession(headers=headers) as aio_session:
        async with aio_session.get(url) as response:
            trends = await response.json()

            await delete_all_trends(session=session)

            retrieved_trends = []

            for trend in trends:
                counter = 0
                for day in trend["history"]:
                    counter += int(day["uses"])
                retrieved_trends.append(TrendModel(
                    id=int(trend["id"]),
                    name=trend["name"],
                    url=trend["url"],
                    uses_in_last_seven_days=counter
                ))

            await update_and_retrieve_trends(session=session, trends=retrieved_trends)


def check_if_trend_exist(session: ScopedSession, name: str):
    query = select(TrendModel).filter(TrendModel.name == name)  # noqa
    result = session.execute(query)
    return result.scalars().one_or_none()


def check_if_suspicious_trend_exist(session: ScopedSession, name: str):
    query = select(SuspiciousTrendModel).filter(SuspiciousTrendModel.name == name)  # noqa
    result = session.execute(query)
    return result.scalars().one_or_none()


async def get_all_trends(session: AsyncSession, page: int, limit: int):
    query = (
        select(TrendModel)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    count_query = (
        select(func.count(TrendModel.id))
        .offset((page - 1) * limit)
        .limit(limit)
    )

    result = await session.execute(query)
    results = await session.execute(count_query)

    total_count = results.scalar()

    pagination = calculate_pagination(page=page, limit=limit, total_count=total_count)
    accounts = result.scalars().all()

    return accounts, pagination


async def get_all_suspicious_trends(session: AsyncSession, page: int, limit: int, instance: str = None):
    query = (
        select(SuspiciousTrendModel)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    count_query = (
        select(func.count(SuspiciousTrendModel.id))
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if instance:
        query = query.filter(SuspiciousTrendModel.instance_url == instance)  # noqa
        count_query = count_query.filter(SuspiciousTrendModel.instance_url == instance)  # noqa

    result = await session.execute(query)
    results = await session.execute(count_query)

    total_count = results.scalar()

    pagination = calculate_pagination(page=page, limit=limit, total_count=total_count)
    accounts = result.scalars().all()

    return accounts, pagination


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
