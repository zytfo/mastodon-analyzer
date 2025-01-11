# stdlib

# thirdparty
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.schemas.common_schema import ResultsResponse
from db.schemas.suspicious_status_schema import SuspiciousStatusSchema
from db.session_manager import get_session
from services.status_service import get_all_suspicious_statuses
from utils.helpers import response_wrapper_results

# project

router = APIRouter(tags=["4. Statuses"], prefix="/statuses")


@router.get("/suspicious", response_model=ResultsResponse[SuspiciousStatusSchema])
async def get_suspicious_statuses(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    session: AsyncSession = Depends(get_session)
):
    """
    Get suspicious statuses
    """
    statuses, pagination = await get_all_suspicious_statuses(
        session=session,
        page=page,
        limit=limit,
    )

    return response_wrapper_results(
        results=statuses,
        pagination=pagination
    )
