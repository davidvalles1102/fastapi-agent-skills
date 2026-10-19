"""Configuración centralizada de la aplicación.

Todos los valores pueden sobrescribirse con variables de entorno, de modo que
no existan constantes "mágicas" repartidas por rutas o servicios.
"""
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str = "Prompt Analyzer API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    min_prompt_chars: int = 10
    max_prompt_chars: int = 4000


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración (cacheada). Se inyecta con Depends()."""
    return Settings(
        min_prompt_chars=int(os.getenv("PROMPT_MIN_CHARS", "10")),
        max_prompt_chars=int(os.getenv("PROMPT_MAX_CHARS", "4000")),
    )
