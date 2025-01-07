# stdlib

# thirdparty
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.schemas.common_schema import ResultsResponse
from db.schemas.instance_schema import InstanceSchema
from db.session_manager import get_session
from services.instance_service import get_all_instances
from utils.helpers import response_wrapper_results

# project

router = APIRouter(tags=["2. Instances"], prefix="/instances")


@router.get("", response_model=ResultsResponse[InstanceSchema])
async def get_instances(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    session: AsyncSession = Depends(get_session)
):
    """
    Get instances
    """
    instances, pagination = await get_all_instances(
        session=session,
        page=page,
        limit=limit,
    )

    return response_wrapper_results(
        results=instances,
        pagination=pagination
    )
