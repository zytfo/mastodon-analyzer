# flake8: noqa
# stdlib
from datetime import datetime
from typing import AsyncGenerator

from openai import AsyncOpenAI
# thirdparty
from sqlalchemy import func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_setup import ScopedSession
from db.models.status_model import RawStatusModel, StatusModel
from db.models.statuses_to_check_model import StatusToCheckModel
from settings import get_settings
from utils.pagination import calculate_pagination

settings = get_settings()

client = AsyncOpenAI(api_key=settings.CHATGPT_API_KEY)


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
    query = select(StatusToCheckModel).filter(StatusToCheckModel.id == status_id)  # noqa
    result = await session.execute(query)
    return result.scalar_one_or_none()


def get_statuses_by_tag(session: ScopedSession, tag: str):
    query = select(StatusModel).filter(func.array_to_string(StatusModel.tags, ",").ilike(func.any(["%" + tag + "%"])))
    result = session.execute(query)
    return result.scalars().all()


async def save_ai_response(session: AsyncSession, status_id: str, ai_response: str):
    query = (
        update(StatusToCheckModel)
        .filter(StatusToCheckModel.id == status_id) # noqa
        .values(
            dict(
                chatgpt_response=ai_response,
                checked_at=datetime.utcnow()
            )
        )
    )
    await session.execute(query)


def build_message_with_prompt(status: dict) -> str:
    return f"""
You are an expert in social media content analysis with specialized knowledge in detecting AI-generated or suspicious posts.
Your task is to analyze the following Mastodon post and evaluate whether it is likely suspicious or AI-generated.
Use the provided parameters to make an informed decision.

**Post Analysis Details:**

1. **Post Text:**
   "{status['content']}"

2. **Author Details:**
   - Number of followers: {status['author_followers_count']}
   - Number of followings: {status['author_following_count']}
   - Total posts written by the author: {status['author_statuses_count']}
   - Date of registration: {status['author_created_at']}

3. **Post Metadata:**
   - Hashtags used in the post: check hashtags in the post text

**Guidelines for Evaluation:**
- Consider whether the post text contains patterns commonly found in AI-generated content, such as unnatural phrasing, repetitive structures, or lack of personal context.
- Assess the author’s activity profile. For instance, a high follower-to-following ratio, a very recent registration date, or an unusually high posting frequency could indicate suspicious behavior.
- Examine the hashtags: Are they relevant to the post's content, or do they appear spammy or unrelated?
- Combine all factors to determine the likelihood of the post being suspicious or AI-generated.

**Response Format:**
- Likelihood of being suspicious (Low, Medium, High):
- Reasons for the assessment (based on the parameters provided):
    """


async def get_ai_response(status: dict) -> AsyncGenerator[str, None]:
    message = build_message_with_prompt(status)

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant, skilled in analyzing social media posts "
                    "to detect AI-generated or suspicious content."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        stream=True,
    )

    all_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            all_content += content
            yield all_content
