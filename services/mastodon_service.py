from datetime import datetime

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.instance_model import InstanceModel
from services.instance_service import (delete_all_instances,
                                       update_and_retrieve_instances)
from settings import get_settings

settings = get_settings()


async def upsert_mastodon_instances(session: AsyncSession):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {settings.INSTANCES_SOCIAL_SECRET}"}
    url = f"{settings.INSTANCES_SOCIAL_ENDPOINT}/api/1.0/instances/list?count=10000&include_down=false&min_active_users=100"
    async with aiohttp.ClientSession(headers=headers) as client_session:
        async with client_session.get(url=url) as response:
            data = await response.json()

            await delete_all_instances(session=session)

            retrieved_instances = []

            for instance in data["instances"]:
                instance["added_at"] = (
                    datetime.strptime(instance["added_at"], "%Y-%m-%dT%H:%M:%S.%fZ") if instance["added_at"] else None
                )
                instance["updated_at"] = (
                    datetime.strptime(instance["updated_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if instance["updated_at"]
                    else None
                )
                instance["checked_at"] = (
                    datetime.strptime(instance["checked_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if instance["checked_at"]
                    else None
                )
                retrieved_instances.append(InstanceModel(**instance))

            await update_and_retrieve_instances(session=session, instances=retrieved_instances)
