from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.instance_model import InstanceModel
from utils.pagination import calculate_pagination


async def delete_all_instances(session: AsyncSession):
    query = delete(InstanceModel)
    await session.execute(query)


async def update_and_retrieve_instances(session: AsyncSession, instances: list):
    session.add_all(instances)

    query = select(InstanceModel)
    result = await session.execute(query)
    return result.scalars().all()


async def get_all_instances(session: AsyncSession, page: int, limit: int):
    query = (
        select(InstanceModel)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    count_query = (
        select(func.count(InstanceModel.id))
        .offset((page - 1) * limit)
        .limit(limit)
    )

    result = await session.execute(query)
    results = await session.execute(count_query)

    total_count = results.scalar()

    pagination = calculate_pagination(page=page, limit=limit, total_count=total_count)
    instances = result.scalars().all()

    return instances, pagination
