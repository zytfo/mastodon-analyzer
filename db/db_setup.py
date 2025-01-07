# stdlib

# thirdparty
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# project
from settings import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL_PSYCOPG2)

Base = declarative_base()

Session = sessionmaker(bind=engine)
ScopedSession = scoped_session(Session)

redis_client = Redis(
    connection_pool=ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=0,
    ),
)
