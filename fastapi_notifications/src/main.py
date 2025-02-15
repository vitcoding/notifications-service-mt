from contextlib import asynccontextmanager

from celery import Celery
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api import router
from core.config import config
from db import redis
from middleware.rate_limiter import RateLimiterMiddleware
from tasks.eventer import eventer_task
from tasks.former import former_task
from tasks.sender import sender_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=config.cache.host, port=config.cache.port)
    yield
    await redis.redis.close()


# App configuration
app = FastAPI(
    lifespan=lifespan,
    title=config.globals.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

# Celery app configuration
celery_app = Celery(
    "celery_app",
    backend="rpc://",
    broker=config.broker.connection,
)

celery_app.conf.beat_schedule = {
    "former-background-task": {
        "task": "tasks.former.former_task",
        "schedule": 2.0,
        "args": ("former-app",),
    },
    "sender-background-task": {
        "task": "tasks.sender.sender_task",
        "schedule": 3.0,
        "args": ("sender-app",),
    },
    "eventer-background-task": {
        "task": "tasks.eventer.eventer_task",
        "schedule": 10.0,
        "args": ("eventer-app",),
    },
}


app.add_middleware(
    RateLimiterMiddleware,
    max_requests_per_window_size=60_000,
    window_size_in_seconds=60,
)

# Router connection to the server
app.include_router(router, prefix="/api")
