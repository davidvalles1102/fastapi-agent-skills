"""Rutas HTTP: solo traducen HTTP <-> servicio, sin lógica de negocio."""
from fastapi import APIRouter, Depends

from app.api.deps import get_analyzer
from app.schemas.prompt import AnalysisResponse, PromptRequest, ValidationResponse
from app.services.prompt_analyzer import PromptAnalyzer

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post(
    "/validate",
    response_model=ValidationResponse,
    summary="Valida longitud y riesgos básicos de un prompt",
    description="Verifica que el prompt no esté vacío, respete los límites de longitud y "
                "no contenga prompt injection, secretos ni datos personales.",
)
def validate_prompt(body: PromptRequest, analyzer: PromptAnalyzer = Depends(get_analyzer)):
    return analyzer.validate(body.prompt)


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analiza la calidad de un prompt y devuelve sugerencias",
    description="Evalúa seis criterios (rol, tarea, contexto, formato, restricciones, ejemplos), "
                "calcula un puntaje 0-100, detecta riesgos y propone mejoras concretas.",
)
def analyze_prompt(body: PromptRequest, analyzer: PromptAnalyzer = Depends(get_analyzer)):
    return analyzer.analyze(body.prompt)
