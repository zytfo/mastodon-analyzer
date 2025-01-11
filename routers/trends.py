# stdlib

# thirdparty
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.schemas.common_schema import ResultsResponse
from db.schemas.trend_schema import SuspiciousTrendSchema, TrendSchema
from db.session_manager import get_session
from services.trends_service import get_all_suspicious_trends, get_all_trends
from utils.helpers import response_wrapper_results

# project

router = APIRouter(tags=["3. Trends"], prefix="/trends")


@router.get("", response_model=ResultsResponse[TrendSchema])
async def get_trends(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    session: AsyncSession = Depends(get_session)
):
    """
    Get trends
    """
    trends, pagination = await get_all_trends(
        session=session,
        page=page,
        limit=limit
    )

    return response_wrapper_results(
        results=trends,
        pagination=pagination
    )


@router.get("/suspicious", response_model=ResultsResponse[SuspiciousTrendSchema])
async def get_suspicious_trends(
    instance: str | None = Query(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    session: AsyncSession = Depends(get_session)
):
    """
    Get suspicious trends
    """
    accounts, pagination = await get_all_suspicious_trends(
        session=session,
        page=page,
        limit=limit,
        instance=instance
    )

    return response_wrapper_results(
        results=accounts,
        pagination=pagination
    )
