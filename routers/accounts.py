# stdlib

# thirdparty
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.schemas.account_schema import AccountSchema
from db.schemas.common_schema import ResultsResponse
from db.session_manager import get_session
from services.account_service import get_accounts
from utils.helpers import response_wrapper_results

# project

router = APIRouter(tags=["1. Accounts"], prefix="/accounts")


@router.get("", response_model=ResultsResponse[AccountSchema])
async def get_suspicious_accounts(
    instance: str | None = Query(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    session: AsyncSession = Depends(get_session)
):
    """
    Get suspicious accounts
    """
    accounts, pagination = await get_accounts(
        session=session,
        page=page,
        limit=limit,
        instance=instance
    )

    return response_wrapper_results(
        results=accounts,
        pagination=pagination
    )
