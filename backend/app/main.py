import logging
from collections.abc import AsyncGenerator
from typing import Any

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from uvicorn.config import LOGGING_CONFIG

from app.api.main import api_router
from app.core.config import settings
from app.utils import custom_generate_unique_id

logger = logging.getLogger("uvicorn")


def configure_sentry() -> None:
    """Configure Sentry SDK if DSN is provided"""
    if settings.SENTRY_DSN:
        env = settings.SENTRY_ENVIRONMENT or settings.ENVIRONMENT

        # Initialize Sentry
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=env,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
            ],
            release=f"{settings.PROJECT_NAME}@0.4.1",  # A remplacer par une version dynamique
        )
        logger.info(f"Sentry initialized in {env} environment")
    else:
        logger.info("Sentry DSN not provided, monitoring disabled")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa ARG001
    """life span events"""
    try:
        logger.info("lifespan start")
        yield
    finally:
        logger.info("lifespan exit")


# Configure Sentry first
configure_sentry()

# init FastAPI with lifespan
app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Include the routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["root"])
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


# Route de test pour Sentry
@app.get("/debug-sentry", tags=["debug"])
async def trigger_error() -> None:
    """Route pour tester l'intégration de Sentry"""
    division_by_zero = 1 / 0
    return division_by_zero  # noqa: F841


# Logger
def timestamp_log_config(uvicorn_log_config: dict[str, Any]) -> dict[str, Any]:
    """https://github.com/fastapi/fastapi/discussions/7457#discussioncomment-5565969"""
    datefmt = "%d-%m-%Y %H:%M:%S"
    formatters = uvicorn_log_config["formatters"]
    formatters["default"]["fmt"] = "%(levelprefix)s [%(asctime)s] %(message)s"
    formatters["access"]["fmt"] = (
        '%(levelprefix)s [%(asctime)s] %(client_addr)s - "%(request_line)s" %(status_code)s'
    )
    formatters["access"]["datefmt"] = datefmt
    formatters["default"]["datefmt"] = datefmt
    return uvicorn_log_config


if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=8000, log_config=timestamp_log_config(LOGGING_CONFIG)
    )
