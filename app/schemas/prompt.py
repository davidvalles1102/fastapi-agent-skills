"""Modelos Pydantic (contratos de entrada y salida) de la API."""
from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["info", "warning", "critical"]
Level = Literal["deficiente", "aceptable", "bueno", "excelente"]


class PromptRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="Texto del prompt que se desea validar o analizar.",
        examples=["Actúa como profesor de bases de datos y explica qué es una llave foránea."],
    )


class Finding(BaseModel):
    code: str = Field(..., description="Código estable del hallazgo, p. ej. PII_EMAIL.")
    severity: Severity
    message: str


class ValidationResponse(BaseModel):
    valid: bool
    char_count: int
    word_count: int
    issues: list[Finding]


class AnalysisResponse(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Puntaje de calidad 0-100.")
    level: Level
    safe_to_send: bool = Field(
        ..., description="False si existe algún hallazgo crítico (injection o secretos)."
    )
    criteria: dict[str, bool] = Field(
        ..., description="Criterios de calidad detectados (rol, tarea, contexto, etc.)."
    )
    findings: list[Finding]
    suggestions: list[str]
    char_count: int
    word_count: int
