from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.instance_model import InstanceModel


async def delete_all_instances(session: AsyncSession):
    query = delete(InstanceModel)
    await session.execute(query)


async def update_and_retrieve_instances(session: AsyncSession, instances: list):
    session.add_all(instances)

    query = select(InstanceModel)
    result = await session.execute(query)
    return result.scalars().all()
