# stdlib
from enum import Enum


class StatusCodeEnum(Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE = 422
    TOO_MANY_REQUESTS = 429
    SERVER_ERROR = 500


class ErrorResponseEnum(Enum):
    INCORRECT_PARAMETERS = (StatusCodeEnum.UNPROCESSABLE, "Incorrect parameters for request")
    INVALID_QUERY_PARAMETERS = (StatusCodeEnum.BAD_REQUEST, "Invalid query parameters")
    SOMETHING_WENT_WRONG = (StatusCodeEnum.BAD_REQUEST, "Something went wrong")

    def __init__(self, http_code, message_en):
        self.http_code = http_code
        self.detail_en = message_en
