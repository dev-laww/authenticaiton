from fastapi import FastAPI
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["200/day", "50/hour"])


def setup_rate_limiting(app: FastAPI):
    """Sets up rate limiting middleware for the FastAPI app."""
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)


def limit(rate: str):
    """Decorator to apply rate limiting to FastAPI routes."""
    return limiter.limit(rate)


__all__ = ["setup_rate_limiting", "limit"]
