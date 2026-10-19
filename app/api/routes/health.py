from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Estado del servicio")
def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Permite a humanos, agentes y skills comprobar que la API está viva."""
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
