# flake8: noqa
# stdlib
from datetime import datetime
from typing import AsyncGenerator

# thirdparty
from sqlalchemy import func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_setup import ScopedSession
from db.models.status_model import RawStatusModel, StatusModel
from db.models.statuses_to_check_model import StatusToCheckModel
from services.llm_provider import LLMModel, LLMProvider
from settings import get_settings
from utils.pagination import calculate_pagination

settings = get_settings()

llm_provider = LLMProvider()


def save_status(session: ScopedSession, status: dict):
    status = dict(**status)
    query = insert(StatusModel).values(status)
    session.execute(query)
    session.commit()


def save_raw_status(session: ScopedSession, status: dict):
    status = dict(**status)
    insert_stmt = postgres_insert(RawStatusModel).values(status)
    insert_stmt = insert_stmt.on_conflict_do_nothing()
    session.execute(insert_stmt)
    session.commit()


def save_status_to_check(session: ScopedSession, status: dict):
    status = dict(**status)
    insert_stmt = postgres_insert(StatusToCheckModel).values(status)
    insert_stmt = insert_stmt.on_conflict_do_nothing()
    session.execute(insert_stmt)
    session.commit()


async def get_all_suspicious_statuses(session: AsyncSession, page: int, limit: int):
    query = (
        select(StatusToCheckModel)
        .order_by(StatusToCheckModel.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    count_query = (
        select(func.count(StatusToCheckModel.id))
        .offset((page - 1) * limit)
        .limit(limit)
    )

    result = await session.execute(query)
    results = await session.execute(count_query)

    total_count = results.scalar()

    pagination = calculate_pagination(page=page, limit=limit, total_count=total_count)
    statuses = result.scalars().all()

    return statuses, pagination


async def get_suspicious_status_by_id(session: AsyncSession, status_id: str):
    status_id_str = str(status_id)

    query = select(StatusToCheckModel).filter(
        StatusToCheckModel.id == status_id_str
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


def get_statuses_by_tag(session: ScopedSession, tag: str):
    query = select(StatusModel).filter(func.array_to_string(StatusModel.tags, ",").ilike(func.any(["%" + tag + "%"])))
    result = session.execute(query)
    return result.scalars().all()


async def save_ai_response(
        session: AsyncSession,
        status_id: str,
        model: LLMModel,
        ai_response: str,
        confidence: float,
        is_suspicious: bool
):
    status_id_str = str(status_id)

    update_fields = {
        "checked_at": datetime.utcnow()
    }

    if model == LLMModel.OPENAI:
        update_fields.update({
            "openai_response": ai_response,
            "openai_confidence": confidence,
            "openai_is_suspicious": is_suspicious
        })
    elif model == LLMModel.CLAUDE:
        update_fields.update({
            "claude_response": ai_response,
            "claude_confidence": confidence,
            "claude_is_suspicious": is_suspicious
        })
    elif model == LLMModel.GEMINI:
        update_fields.update({
            "gemini_response": ai_response,
            "gemini_confidence": confidence,
            "gemini_is_suspicious": is_suspicious
        })
    elif model == LLMModel.LLAMA:
        update_fields.update({
            "llama_response": ai_response,
            "llama_confidence": confidence,
            "llama_is_suspicious": is_suspicious
        })

    query = (
        update(StatusToCheckModel)
        .where(StatusToCheckModel.id == status_id_str)
        .values(update_fields)
        .execution_options(synchronize_session=False)
    )

    await session.execute(query)
    await session.flush()


async def get_ai_response(status: dict, model: LLMModel) -> AsyncGenerator[str, None]:
    async for result in llm_provider.analyze(status, model):
        yield result
