import logging

from fastapi import FastAPI

from internal.api.middleware import add_exception_handlers, add_middleware
from internal.api.router import api_router
from internal.config.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)

    app = FastAPI(title="Ascend NPU Resource Platform")
    add_exception_handlers(app)
    add_middleware(app)
    app.include_router(api_router)
    return app


app = create_app()
