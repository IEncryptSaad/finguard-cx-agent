import contextvars
import logging

from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import Headers
from starlette.responses import Response

logger = logging.getLogger(__name__)
_preflight_path = contextvars.ContextVar("cors_preflight_path", default=None)


class LoggingCORSMiddleware(CORSMiddleware):
    async def __call__(self, scope, receive, send):
        path = scope.get("path") if scope.get("type") == "http" else None
        token = _preflight_path.set(path)
        try:
            await super().__call__(scope, receive, send)
        finally:
            _preflight_path.reset(token)

    def preflight_response(self, request_headers: Headers) -> Response:
        response = super().preflight_response(request_headers)
        if response.status_code == 400:
            origin = request_headers.get("origin")
            requested_method = request_headers.get("access-control-request-method")
            requested_headers = request_headers.get("access-control-request-headers")
            reason = response.body.decode("utf-8")
            path = _preflight_path.get()
            logger.warning(
                "CORS preflight rejected "
                "origin=%s requested_method=%s requested_headers=%s reason=%s path=%s",
                origin,
                requested_method,
                requested_headers,
                reason,
                path,
                extra={
                    "origin": origin,
                    "access_control_request_method": requested_method,
                    "access_control_request_headers": requested_headers,
                    "reason": reason,
                    "path": path,
                },
            )
        return response
