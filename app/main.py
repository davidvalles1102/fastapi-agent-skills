"""Punto de entrada: ensambla la aplicación (patrón application factory)."""
from fastapi import FastAPI

from app.api.routes import health, prompts
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API que valida y analiza prompts. Diseñada para ser consumida por un "
                    "agente de IA mediante la skill `prompt-analyzer-api`.",
    )
    app.include_router(health.router)
    app.include_router(prompts.router, prefix=settings.api_prefix)
    return app


app = create_app()
