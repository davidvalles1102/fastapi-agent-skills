"""Dependencias inyectables (Depends) compartidas por las rutas."""
from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.prompt_analyzer import PromptAnalyzer


def get_analyzer(settings: Settings = Depends(get_settings)) -> PromptAnalyzer:
    return PromptAnalyzer(settings)
