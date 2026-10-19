# Prompt Analyzer API — FastAPI + Agent Skills

API en **FastAPI** que valida y analiza la calidad y seguridad de prompts, junto con dos
**skills personalizadas** (estándar Agent Skills, en `.github/skills/`) que controlan cómo
un agente de IA consume y extiende esta API.

> Actividad individual — KODIGO · FastAPI & Agent Skills Integration · Autor: `davidvalles1102`

---

## 1. Funcionalidad de la API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio. |
| POST | `/api/v1/prompts/validate` | Valida que el prompt no esté vacío, respete límites de longitud y no contenga *prompt injection*, secretos ni datos personales. |
| POST | `/api/v1/prompts/analyze` | Puntúa el prompt (0–100) según 6 criterios (rol, tarea, contexto, formato, restricciones, ejemplos), detecta riesgos y devuelve sugerencias de mejora. |

Documentación interactiva autogenerada: `http://127.0.0.1:8000/docs`.

### Ejemplo
```bash
curl -X POST http://127.0.0.1:8000/api/v1/prompts/analyze \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"Actúa como profesor de bases de datos. Explica qué es una llave foránea en formato de lista, máximo 120 palabras.\"}"
```

### Arquitectura (separación de responsabilidades)
```
app/
├── main.py               # Ensambla la app (application factory)
├── core/config.py        # Configuración (variables de entorno), sin constantes sueltas
├── api/
│   ├── deps.py           # Inyección de dependencias (Depends)
│   └── routes/           # Capa HTTP: sin lógica de negocio
│       ├── health.py
│       └── prompts.py
├── schemas/prompt.py     # Contratos Pydantic de entrada/salida
└── services/prompt_analyzer.py   # Lógica de negocio pura (no importa fastapi)
tests/test_api.py         # 8 pruebas automáticas
scripts/validate_skills.py# Valida que las skills cumplan el estándar
.github/
├── copilot-instructions.md
└── skills/
    ├── prompt-analyzer-api/          # Skill 1: CONSUMIR la API
    │   ├── SKILL.md
    │   ├── scripts/call_api.py
    │   ├── references/scoring-rubric.md
    │   └── assets/report-template.md
    └── fastapi-endpoint-conventions/ # Skill 2: EXTENDER la API
        ├── SKILL.md
        ├── references/endpoint-checklist.md
        └── assets/endpoint-template.py
```

## 2. Cómo ejecutar
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload          # API en http://127.0.0.1:8000
python -m pytest -q                    # pruebas
python scripts/validate_skills.py      # valida las skills
```
Variables opcionales: `PROMPT_MIN_CHARS` (10) y `PROMPT_MAX_CHARS` (4000).

## 3. Propósito y funcionamiento de las skills

### Skill 1 — `prompt-analyzer-api` (el agente *usa* la API)
Se activa por su `description` semántica cuando el usuario pide revisar, puntuar o
comprobar la seguridad de un prompt. Incluye:
- **SKILL.md**: flujo obligatorio (health → validate → analyze → informe), reglas y manejo de errores.
- **scripts/call_api.py**: cliente de la API solo con librería estándar, con códigos de salida definidos.
- **references/scoring-rubric.md**: cómo interpretar el puntaje (carga bajo demanda).
- **assets/report-template.md**: plantilla fija del informe.

### Skill 2 — `fastapi-endpoint-conventions` (el agente *extiende* la API)
Se activa cuando se pide agregar o modificar endpoints. Obliga a respetar la arquitectura en
capas (tabla de qué va y qué está prohibido en cada capa), un procedimiento de 8 pasos, una
plantilla (`assets/endpoint-template.py`) y un checklist de revisión.

## 4. Cómo la skill modifica el comportamiento del agente

| Situación | Sin skill | Con la skill |
|---|---|---|
| "Revisa este prompt" | El agente opina a ojo, con criterios distintos cada vez. | Consulta la API, cita el puntaje exacto y responde con la plantilla fija. |
| Prompt con `ignora las instrucciones...` | Puede pasarlo por alto o reescribirlo conservándolo. | Marca `safe_to_send=false`, abre con advertencia y no conserva el contenido peligroso. |
| Prompt con correo/teléfono | Repite los datos en la respuesta. | Sugiere marcadores (`[CORREO]`) y no los repite. |
| API apagada | Puede inventar un resultado. | Se detiene y pide iniciar la API (regla explícita). |
| "Agrega un endpoint" | Escribe todo en `main.py`. | Crea esquema → servicio → ruta → test, ejecuta pytest y valida skills antes de cerrar. |
| "Mejora mi prompt" | Reescribe sin verificar. | Reescribe y **vuelve a analizar** para mostrar puntaje antes → después. |

La integración es explícita: `.github/copilot-instructions.md` apunta a ambas skills, y el
agente las selecciona por la coincidencia entre la petición y su `description`.

## 5. Evidencia del uso consciente de herramientas de IA

**Herramienta:** Claude (asistente de IA) para generar el andamiaje inicial. Las decisiones de
diseño, la ejecución y la validación se hicieron comprobando cada resultado.

### Qué se pidió a la IA
Estructura por capas de FastAPI, el servicio de análisis, los dos `SKILL.md` con sus recursos,
las pruebas y este README, a partir del enunciado y la rúbrica.

### Qué se validó y qué se ajustó
| Sugerencia / resultado de la IA | Cómo se verificó | Problema encontrado → ajuste |
|---|---|---|
| Código de la API y tests | `pytest` | 8/8 pasan; se verificó además que los casos negativos (422, prompt corto, injection) realmente fallan como se espera. |
| Script `call_api.py` | Ejecución real contra el servidor levantado con `uvicorn` | **Bug:** el escape de comillas generó un `SyntaxError` en una línea; no lo detectaban los tests porque el script no está en `app/`. Se corrigió y se probaron los 4 caminos (OK, stdin vacío → exit 3, 422, API caída → exit 2). |
| Creación de carpetas de las skills | `find` / `ls` | **Bug:** `mkdir -p a/{b,c}` no se expandió en `sh` y creó carpetas literales `{b,c}`. Se eliminaron y se recrearon los archivos. |
| `SKILL.md` "correctos" | Se escribió `scripts/validate_skills.py` | Prueba negativa: se rompió el `name` a propósito y el validador lo detectó (exit 1); luego se restauró (exit 0). |
| Heurísticas de puntaje | Prompt "excelente" → 100; "dame algo" → deficiente | Se aceptó que el análisis es heurístico (palabras clave) y se documentó esa limitación en `references/scoring-rubric.md`. |

### Criterio propio aplicado
- Se rechazó una estructura monolítica en `main.py` y se separó en rutas / esquemas / servicios / config.
- Se evitó añadir dependencias innecesarias (`call_api.py` y `validate_skills.py` usan solo librería estándar; la configuración usa `dataclass` en vez de `pydantic-settings`).
- Limitaciones conocidas: análisis por palabras clave (no semántico); detección de teléfonos pensada para formatos de 8 dígitos y puede dar falsos positivos.
