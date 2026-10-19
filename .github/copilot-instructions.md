# Instrucciones para agentes en este repositorio

Proyecto: API FastAPI "Prompt Analyzer". Idioma de respuesta: español.

Skills disponibles en `.github/skills/` (se cargan por la coincidencia con su `description`):
- `prompt-analyzer-api`: para analizar/validar prompts consultando la API.
- `fastapi-endpoint-conventions`: para agregar o modificar endpoints respetando las capas.

Antes de cerrar cualquier cambio de código ejecuta `python -m pytest -q`
y `python scripts/validate_skills.py`.
