"""Plantilla: copiar cada bloque a su capa correspondiente y renombrar."""

# ---- app/schemas/<recurso>.py ----
from pydantic import BaseModel, Field


class ExampleRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto de entrada.")


class ExampleResponse(BaseModel):
    result: str


# ---- app/services/<recurso>.py ----
from app.core.config import Settings


class ExampleService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def run(self, text: str) -> ExampleResponse:
        return ExampleResponse(result=text.upper())


# ---- app/api/deps.py ----
from fastapi import Depends

from app.core.config import get_settings


def get_example_service(settings: Settings = Depends(get_settings)) -> ExampleService:
    return ExampleService(settings)


# ---- app/api/routes/<recurso>.py ----
from fastapi import APIRouter

router = APIRouter(prefix="/examples", tags=["examples"])


@router.post("", response_model=ExampleResponse, summary="Resumen corto")
def run_example(body: ExampleRequest, service: ExampleService = Depends(get_example_service)):
    return service.run(body.text)
