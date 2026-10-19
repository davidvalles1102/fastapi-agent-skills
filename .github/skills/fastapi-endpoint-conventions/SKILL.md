---
name: fastapi-endpoint-conventions
description: Convenciones obligatorias para crear o modificar endpoints en este proyecto FastAPI (rutas, esquemas Pydantic, servicios, configuración y tests). Úsala cuando el usuario pida agregar, cambiar o refactorizar un endpoint, ruta, esquema o servicio de la API. No la uses para consumir la API ni para analizar prompts.
license: MIT
compatibility: Proyecto Python 3.10+ con FastAPI y pytest.
metadata:
  author: davidvalles1102
  version: "1.0"
---

# Convenciones de endpoints FastAPI

Esta skill obliga al agente a respetar la arquitectura en capas del proyecto en lugar
de poner todo en un solo archivo.

## Arquitectura (no negociable)
| Capa | Carpeta | Responsabilidad | Prohibido |
|---|---|---|---|
| Rutas | `app/api/routes/` | Traducir HTTP ↔ servicio | Lógica de negocio, regex, cálculos |
| Esquemas | `app/schemas/` | Contratos de entrada/salida (Pydantic) | Lógica |
| Servicios | `app/services/` | Lógica de negocio pura | Importar `fastapi` |
| Config | `app/core/config.py` | Valores configurables | Constantes sueltas en otras capas |
| Dependencias | `app/api/deps.py` | Inyección con `Depends` | — |

## Pasos para agregar un endpoint
1. **Esquema**: crea los modelos de request/response en `app/schemas/` con `Field(description=...)`.
2. **Servicio**: implementa la lógica en `app/services/` como método de una clase; recibe `Settings` por constructor.
3. **Dependencia**: expón el servicio en `app/api/deps.py` si es nuevo.
4. **Ruta**: crea la función en `app/api/routes/` con `response_model`, `summary` y `description`; la función no debe tener más de ~3 líneas.
5. **Registro**: incluye el router en `app/main.py` si el archivo de rutas es nuevo.
6. **Tests**: agrega al menos un caso feliz, un caso de error y un caso 422 en `tests/`.
7. **Verificación**: ejecuta `python -m pytest -q` y `python scripts/validate_skills.py`. No des la tarea por terminada si falla algo.
8. **Documentación**: actualiza la tabla de endpoints del `README.md`.

Usa [assets/endpoint-template.py](assets/endpoint-template.py) como punto de partida y
[references/endpoint-checklist.md](references/endpoint-checklist.md) para la revisión final.

## Reglas de estilo
- Rutas bajo el prefijo `settings.api_prefix` (`/api/v1`), en minúsculas y sustantivos en plural.
- POST para operaciones con cuerpo; GET solo para lecturas sin efectos.
- Códigos de estado explícitos y errores con `HTTPException` (nunca `return {"error": ...}` con 200).
