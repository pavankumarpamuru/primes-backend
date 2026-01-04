from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.observability.custom_metrics import record_http_error


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    record_http_error(status.HTTP_400_BAD_REQUEST, str(request.url.path))
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"code": "INVALID_INPUT"}},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    record_http_error(status.HTTP_500_INTERNAL_SERVER_ERROR, str(request.url.path))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_SERVER_ERROR"}},
    )
