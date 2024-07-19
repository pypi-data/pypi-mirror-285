import os
import inspect
import logging
import uvicorn
from fastapi.middleware import Middleware
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
from package.app.models import (
    sessionmanager,
    get_db_session,
)
from package.app import api as a_app
from fastapi import FastAPI
from mrkutil.logging import get_logging_config

log_level = os.getenv("LOG_LEVEL", "DEBUG")
develop = bool("true" == str(os.getenv("DEVELOP", "false")).lower())
json_format = bool("true" == str(os.getenv("JSON_FORMAT", "false")).lower())

logging_config = get_logging_config(log_level, json_format, True)
logging.config.dictConfig(logging_config)
logger = logging.getLogger("main")

API_STR = os.getenv("API_ROOT", "/api")
develop = str(os.getenv("DEVELOP", "False")).lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


allowed_hosts = os.getenv("ALLOWED_HOSTS", "*")
if allowed_hosts != "*":
    allowed_hosts = allowed_hosts.split(",")


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
]

app = FastAPI(
    lifespan=lifespan,
    middleware=middleware,
    debug=develop,
)

for name, obj in inspect.getmembers(a_app):
    if "_router" in name:
        app.include_router(obj, prefix=API_STR)


def dev():
    uvicorn.run(
        "package.app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level=log_level.lower(),
        log_config=logging_config,
    )


def prod():
    uvicorn.run(
        "package.app.main:app",
        headers=[
            ("server", "Apache"),
            ("X-Frame-Options", "SAMEORIGIN"),
            ("X-XSS-Protection", "1; mode=block"),
            ("X-Content-Type-Options", "nosniff"),
            ("Strict-Transport-Security", "max-age=15768000; includeSubDomains"),
            ("Referrer-Policy", "no-referrer-when-downgrade"),
            ("Content-Security-Policy", "frame-ancestors 'self'"),
        ],
        host="0.0.0.0",
        port=80,
        log_level=log_level.lower(),
        log_config=logging_config,
        forwarded_allow_ips="*",
    )


class DBSessionContextManager:
    def __init__(self):
        self._session_generator = get_db_session()
        self._session = None

    async def __aenter__(self):
        self._session = await self._session_generator.__anext__()
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.close()


if __name__ == "__main__":
    logger.info("Rest API application up and running!")
    dev() if develop else prod()
