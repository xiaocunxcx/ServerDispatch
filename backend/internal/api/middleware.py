from __future__ import annotations

import logging
import threading
import time
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from internal.api.errors import ApiError, ErrorResponse
from internal.audit.middleware import AuditLogMiddleware
from internal.config.settings import get_settings


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logging.info(
            "%s %s %s %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self._buckets: dict[str, tuple[float, int]] = {}

    def allow(self, key: str) -> tuple[bool, float]:
        now = time.monotonic()
        with self._lock:
            reset_at, count = self._buckets.get(key, (now + self.window_seconds, 0))
            if now >= reset_at:
                reset_at = now + self.window_seconds
                count = 0
            if count >= self.limit:
                self._buckets[key] = (reset_at, count)
                return False, reset_at
            self._buckets[key] = (reset_at, count + 1)
            return True, reset_at


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        settings = get_settings()
        window_seconds = max(settings.rate_limit_window_seconds, 1)
        self._login_limiter = RateLimiter(
            settings.rate_limit_login_per_minute, window_seconds
        )
        self._reservation_limiter = RateLimiter(
            settings.rate_limit_reservation_per_minute, window_seconds
        )

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path
        limiter: RateLimiter | None = None

        if path == "/auth/login":
            limiter = self._login_limiter
        elif path.startswith("/reservations"):
            limiter = self._reservation_limiter

        if limiter and limiter.limit > 0:
            client_host = request.client.host if request.client else "unknown"
            allowed, reset_at = limiter.allow(f"{client_host}:{path}")
            if not allowed:
                retry_after = max(1, int(reset_at - time.monotonic()))
                payload = ErrorResponse(code="rate_limited", message="Too many requests")
                return JSONResponse(
                    status_code=429,
                    content=payload.model_dump(),
                    headers={"Retry-After": str(retry_after)},
                )

        return await call_next(request)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(_: Request, exc: ApiError) -> JSONResponse:
        payload = ErrorResponse(code=exc.code, message=exc.message)
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


def add_middleware(app: FastAPI) -> None:
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(AuditLogMiddleware)
    app.add_middleware(RateLimitMiddleware)
