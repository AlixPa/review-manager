import contextlib

from asgi_correlation_id.middleware import CorrelationIdMiddleware, is_valid_uuid4
from fastapi import FastAPI

from .api import api_router
from .config.env import ENV, ServiceEnv


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url=None if ENV == ServiceEnv.PRODUCTION else "/docs",
    redoc_url=None if ENV == ServiceEnv.PRODUCTION else "/redoc",
    openapi_url=None if ENV == ServiceEnv.PRODUCTION else "/openapi.json",
)

app.include_router(api_router)


app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Correlation-ID",
    update_request_header=True,
    validator=is_valid_uuid4 if ENV == ServiceEnv.PRODUCTION else None,
)
