# stdlib
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_setup import ScopedSession
from db.models.account_model import AccountModel
from utils.pagination import calculate_pagination


async def get_accounts(session: AsyncSession, page: int, limit: int, instance: str = None):
    query = (
        select(AccountModel)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    count_query = (
        select(func.count(AccountModel.id))
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if instance:
        query = query.filter(AccountModel.instance_url == instance)  # noqa
        count_query = count_query.filter(AccountModel.instance_url == instance)  # noqa

    result = await session.execute(query)
    results = await session.execute(count_query)

    total_count = results.scalar()

    pagination = calculate_pagination(page=page, limit=limit, total_count=total_count)
    accounts = result.scalars().all()

    return accounts, pagination


def create_or_update_account(session: ScopedSession, account: dict, instance_url: str):
    insert_stmt = insert(AccountModel).values(**account)

    insert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["acct"],
        set_=dict(
            locked=account["locked"],
            bot=account["bot"],
            discoverable=account["discoverable"],
            group=account["group"],
            note=account["note"],
            url=account["url"],
            avatar=account["avatar"],
            avatar_static=account["avatar_static"],
            header=account["header"],
            header_static=account["header_static"],
            followers_count=account["followers_count"],
            following_count=account["following_count"],
            statuses_count=account["statuses_count"],
            last_status_at=account["last_status_at"],
            instance_url=instance_url,
        ),
    )

    return session.execute(insert_stmt)
