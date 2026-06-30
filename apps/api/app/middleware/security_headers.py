DOCS_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
    "img-src 'self' data: https:; "
    "font-src 'self' cdn.jsdelivr.net data:"
)
STRICT_CSP = "default-src 'self'"


async def security_headers_middleware(request, call_next):
    response = await call_next(request)
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Referrer-Policy', 'no-referrer')
    response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
    csp = DOCS_CSP if request.url.path in {'/api/v1/docs', '/api/v1/redoc'} else STRICT_CSP
    response.headers.setdefault('Content-Security-Policy', csp)
    return response
