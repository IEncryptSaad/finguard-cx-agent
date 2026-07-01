import logging

from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import Headers
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingCORSMiddleware(CORSMiddleware):
    def preflight_response(self, request_headers: Headers) -> Response:
        response = super().preflight_response(request_headers)
        if response.status_code == 400:
            logger.warning(
                "CORS preflight rejected",
                extra={
                    "origin": request_headers.get("origin"),
                    "access_control_request_method": request_headers.get("access-control-request-method"),
                    "access_control_request_headers": request_headers.get("access-control-request-headers"),
                    "reason": response.body.decode("utf-8"),
                },
            )
        return response
