# stdlib
import asyncio
import logging
from contextlib import asynccontextmanager

import nltk
# thirdparty
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from db.session_manager import db_manager
# project
from routers import accounts, instances, trends
from services.listener import listen_mastodon_stream
from services.mastodon_service import upsert_mastodon_instances
from services.trends_service import update_mastodon_trends
from settings import get_settings
from utils.helpers import (CustomHTTPException, custom_exception_handler,
                           general_exception_handler,
                           validation_exception_handler)
from utils.logging import logger, setup_logging

setup_logging(logging.INFO)

settings = get_settings()

router = APIRouter(prefix="/api/v1")

nltk.download('punkt')


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    db_manager.init(settings.DATABASE_URL)
    task = asyncio.create_task(listen_mastodon_stream())

    async with db_manager.session() as session:
        await upsert_mastodon_instances(session=session)
        await update_mastodon_trends(session=session)
        pass
    yield

    logger.info("Shutting down Mastodon stream.")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Mastodon stream listener shut down gracefully.")

    await db_manager.close()


app = FastAPI(
    title="Mastodon Analyzer API",
    version="0.0.1",
    lifespan=lifespan,
    docs_url=None if settings.ENV == "prod" else "/docs",
    redoc_url=None,
    openapi_url=None if settings.ENV == "prod" else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router.include_router(accounts.router)
router.include_router(instances.router)
router.include_router(trends.router)
app.include_router(router)


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /metrics") == -1


class Non200Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.getMessage().endswith("200")


class Non400Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.getMessage().endswith("400")


class Non401Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.getMessage().endswith("401")


class Non403Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.getMessage().endswith("403")


class Non404Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.getMessage().endswith("404")


class Non422Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.getMessage().endswith("422")


logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
logging.getLogger("uvicorn.access").addFilter(Non200Filter())
logging.getLogger("uvicorn.access").addFilter(Non400Filter())
logging.getLogger("uvicorn.access").addFilter(Non401Filter())
logging.getLogger("uvicorn.access").addFilter(Non403Filter())
logging.getLogger("uvicorn.access").addFilter(Non404Filter())
logging.getLogger("uvicorn.access").addFilter(Non422Filter())

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(CustomHTTPException, custom_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


def openapi_specs():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Mastodon Analyzer",
        version="1.0.0",
        description="Mastodon Analyzer Open-API Specification",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = openapi_specs

info_app = f"""
    Mastodon Analyzer API - VERSION: 0.0.1
    OpenAPI: {app.openapi_url}
"""

logger.info(info_app)

# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host=settings.HOST,
#         port=settings.PORT,
#     )
