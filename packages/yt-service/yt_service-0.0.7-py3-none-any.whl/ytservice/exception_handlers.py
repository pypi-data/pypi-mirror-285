import typing

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ytservice.common import build_response, RESULT_CODE_ERROR


# Helper function to format exception messages
def format_exception_message(exc: typing.Any) -> str:
    if isinstance(exc, RequestValidationError):
        return "; ".join([error['msg'] for error in exc.errors()])
    elif isinstance(exc, HTTPException):
        return exc.detail
    return "Internal server error"


# Exception handler for validation errors
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=build_response(code=RESULT_CODE_ERROR, message=format_exception_message(exc))
    )


# Exception handler for HTTP exceptions
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=build_response(code=RESULT_CODE_ERROR, message=format_exception_message(exc))
    )


# Exception handler for general exceptions
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=build_response(code=RESULT_CODE_ERROR, message=format_exception_message(exc))
    )
