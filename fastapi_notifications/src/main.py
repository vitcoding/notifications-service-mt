from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import router
from core.config import config
from middleware.rate_limiter import RateLimiterMiddleware

# from redis.asyncio import Redis
# from db import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    yield
    # await redis.redis.close()


# App configuration
app = FastAPI(
    lifespan=lifespan,
    title=config.globals.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    RateLimiterMiddleware,
    max_requests_per_window_size=20,
    window_size_in_seconds=60,
)

# Router connection to the server
app.include_router(router, prefix="/api")
