# stdlib
import asyncio
import json
import logging
from contextlib import asynccontextmanager

import nltk
# thirdparty
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.websockets import WebSocket, WebSocketDisconnect

from db.session_manager import db_manager
# project
from routers import accounts, instances, statuses, trends
from services.listener import listen_mastodon_stream
from services.llm_provider import LLMModel, extract_json_and_confidence
from services.mastodon_service import upsert_mastodon_instances
from services.status_service import (get_ai_response,
                                     get_suspicious_status_by_id,
                                     save_ai_response)
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
nltk.download('punkt_tab')


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    db_manager.init(settings.DATABASE_URL)
    # task = asyncio.create_task(listen_mastodon_stream())
    #
    # async with db_manager.session() as session:
    #     await upsert_mastodon_instances(session=session)
    #     await update_mastodon_trends(session=session)
    #     pass
    yield

    logger.info("Shutting down Mastodon stream.")
    # task.cancel()
    # try:
    #     await task
    # except asyncio.CancelledError:
    #     logger.info("Mastodon stream listener shut down gracefully.")

    await db_manager.close()


app = FastAPI(
    title="Mastodon Analyzer API",
    version="0.0.1",
    lifespan=lifespan,
    # docs_url=None if settings.ENV == "prod" else "/docs",
    docs_url="/docs",
    redoc_url=None,
    # openapi_url=None if settings.ENV == "prod" else "/openapi.json",
    openapi_url="/openapi.json",
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
router.include_router(statuses.router)
app.include_router(router)


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    """
    Websocket endpoint для анализа постов

    Клиент отправляет JSON:
    {
        "status_id": "123456",
        "model": "openai"
    }
    """
    await websocket.accept()

    try:
        while True:
            message_text = await websocket.receive_text()

            try:
                message_data = json.loads(message_text)
                status_id = str(message_data.get("status_id"))
                model_name = message_data.get("model", "openai").lower()

                try:
                    model = LLMModel(model_name)
                except ValueError:
                    await websocket.send_text(json.dumps({
                        "error": f"Invalid model. Available: {[m.value for m in LLMModel]}"
                    }))
                    continue

            except json.JSONDecodeError:
                status_id = str(message_text)
                model = LLMModel.OPENAI

            async with db_manager.session() as session:
                status = await get_suspicious_status_by_id(session=session, status_id=status_id)

                if not status:
                    await websocket.send_text(json.dumps({
                        "error": "Status not found",
                        "status_id": status_id
                    }))
                    continue

                status_dict = status.__dict__
                status_dict.pop('_sa_instance_state', None)

                await websocket.send_text(json.dumps({
                    "type": "start",
                    "model": model.value,
                    "status_id": status_id
                }))

                final_response = ""
                try:
                    async for text in get_ai_response(status=status_dict, model=model):
                        final_response = text
                        await websocket.send_text(json.dumps({
                            "type": "stream",
                            "content": text
                        }))
                except Exception as stream_error:
                    logger.error(f"Streaming error: {str(stream_error)}", exc_info=True)
                    await websocket.send_text(json.dumps({
                        "error": f"Streaming error: {str(stream_error)}"
                    }))
                    continue

                _, confidence, is_suspicious = extract_json_and_confidence(final_response)

                try:
                    await save_ai_response(
                        session=session,
                        status_id=status_id,
                        model=model,
                        ai_response=final_response,
                        confidence=confidence,
                        is_suspicious=is_suspicious
                    )
                    await session.commit()
                except Exception as save_error:
                    logger.error(f"Save error: {str(save_error)}", exc_info=True)
                    await session.rollback()

                await websocket.send_text(json.dumps({
                    "type": "complete",
                    "model": model.value,
                    "confidence": confidence,
                    "is_suspicious": is_suspicious
                }))

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({
                "error": str(e)
            }))
        except Exception:
            pass


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
