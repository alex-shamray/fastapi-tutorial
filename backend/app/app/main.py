import sentry_sdk
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.api.api_v1.routers.utils import health_check
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
app.get(f"{settings.API_V1_STR}/health_check/")(health_check)
app.mount("/static", StaticFiles(directory="static"), name="static")

# https://docs.sentry.io/platforms/python/guides/asgi/
sentry_sdk.init(dsn=settings.SENTRY_DSN)
app = SentryAsgiMiddleware(app)
