from typing import Callable

import redis
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from app import settings


class RateLimiter:
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        max_requests: int = 5,
        window_seconds: int = 900,
    ):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_rate_limited(self, key: str) -> tuple[bool, int, int]:
        try:
            current = self.redis_client.get(key)

            if current is None:
                self.redis_client.set(key, 1, ex=self.window_seconds)
                return False, 1, self.window_seconds

            current_count = int(current)

            if current_count >= self.max_requests:
                ttl = self.redis_client.ttl(key)
                return True, current_count, ttl

            self.redis_client.incr(key)
            ttl = self.redis_client.ttl(key)
            return False, current_count + 1, ttl

        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return False, 0, 0


rate_limiter = RateLimiter(
    redis_url=settings.REDIS_URL,
    max_requests=settings.LOGIN_RATE_LIMIT_REQUESTS,
    window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW,
)


RATE_LIMITED_ENDPOINTS = [
    "/api/v1/auth/login",
]


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    endpoint = request.url.path

    if endpoint not in RATE_LIMITED_ENDPOINTS:
        return await call_next(request)

    rate_limit_key = f"rate_limit:{endpoint}"

    is_limited, current_count, time_remaining = rate_limiter.is_rate_limited(
        rate_limit_key
    )

    if is_limited:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests. Try again in {time_remaining} seconds.",
                    "retry_after": time_remaining,
                }
            },
            headers={"Retry-After": str(time_remaining)},
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(
        rate_limiter.max_requests - current_count
    )
    response.headers["X-RateLimit-Reset"] = str(time_remaining)

    return response
