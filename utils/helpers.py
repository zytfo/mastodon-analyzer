# stdlib
import traceback
from datetime import date, datetime

# thirdparty
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

# project
from settings import get_settings
from utils.errors import ErrorResponseEnum
from utils.logging import logger

settings = get_settings()


def response_wrapper_result(result, status_code=status.HTTP_200_OK):
    response = {"result": jsonable_encoder(result)}
    return JSONResponse(content=response, status_code=status_code)


def response_wrapper_results(results, status_code=status.HTTP_200_OK, pagination=None):
    response = {"results": jsonable_encoder(results)}
    if pagination:
        response["pagination"] = pagination
    return JSONResponse(content=response, status_code=status_code)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class CustomHTTPException(Exception):
    def __init__(self, error_response: ErrorResponseEnum):
        self.error_response = error_response


class PaginationModel(BaseModel):
    page: int
    pages: int
    on_page: int
    total_results: int


def generate_error_response_content(
        error_response: ErrorResponseEnum, exc: ValidationError = None, traceback: str = None
):
    response = dict(code=error_response.name, message_en=error_response.detail_en, message_ru=error_response.detail_ru)

    if exc:
        response.update(dict(details=exc.errors()))

    # output traceback in case it enabled
    if traceback and settings.TRACEBACK_OUTPUT_ENABLED:
        response.update(dict(traceback=traceback))

    return jsonable_encoder(response)


def get_custom_error_response(error_response: ErrorResponseEnum):
    return JSONResponse(
        status_code=error_response.http_code.value,
        content=generate_error_response_content(error_response=error_response),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=ErrorResponseEnum.INVALID_QUERY_PARAMETERS.http_code.value,
        content=generate_error_response_content(error_response=ErrorResponseEnum.INVALID_QUERY_PARAMETERS, exc=exc),
    )


async def custom_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.error_response.http_code.value,
        content=generate_error_response_content(error_response=exc.error_response),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Error: {exc}\n{traceback.format_exc()}")

    return JSONResponse(
        status_code=ErrorResponseEnum.SOMETHING_WENT_WRONG.http_code.value,
        content=generate_error_response_content(
            error_response=ErrorResponseEnum.SOMETHING_WENT_WRONG, traceback=traceback.format_exc()
        ),
    )
