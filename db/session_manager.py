# stdlib
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional
from uuid import uuid4

# thirdparty
from asyncpg import Connection
from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.pool import NullPool


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid4()}__"


class DatabaseSessionManager:
    def __init__(self) -> None:
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None

    def init(self, db_url: str) -> None:
        # Just additional example of customization.
        # you can add parameters to init and so on
        if "postgresql" in db_url:
            # These settings are needed to work with pgbouncer in transaction mode
            # because you can't use prepared statements in such case
            connect_args = {
                # "statement_cache_size": 0,
                # "prepared_statement_cache_size": 0,
                # "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
            }
        else:
            connect_args = {}
        self._engine = create_async_engine(
            url=db_url, pool_pre_ping=True, connect_args=connect_args, poolclass=NullPool
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise


db_manager = DatabaseSessionManager()


async def get_session() -> AsyncIterator[AsyncSession]:
    # This is Fastapi dependency
    # session: AsyncSession = Depends(get_session)
    async with db_manager.session() as session:
        yield session
