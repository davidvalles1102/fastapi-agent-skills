---
name: prompt-analyzer-api
description: Evalúa, puntúa y valida prompts consultando la API local Prompt Analyzer (FastAPI). Úsala cuando el usuario pida revisar, analizar, calificar, mejorar o comprobar la seguridad de un prompt, incluida la detección de prompt injection, datos personales (correo, teléfono) o secretos (API keys). No la uses para ejecutar el prompt, traducir texto ni para preguntas generales sobre IA.
license: MIT
compatibility: Requiere Python 3.10+ y la API en ejecución (uvicorn app.main:app). URL por defecto http://127.0.0.1:8000, configurable con PROMPT_API_URL.
metadata:
  author: davidvalles1102
  version: "1.0"
---

# Prompt Analyzer API

Esta skill cambia la forma en que el agente trabaja con prompts: en lugar de opinar
"a ojo", **siempre consulta la API** y basa su respuesta en los datos devueltos.

## Cuándo activarla
- "Revisa / analiza / califica este prompt"
- "¿Es seguro enviar este texto a un modelo?"
- "Mejora mi prompt" (primero se analiza, luego se reescribe)

## Flujo obligatorio
1. **Comprobar la API**: `python .github/skills/prompt-analyzer-api/scripts/call_api.py health`.
   Si falla, no inventes resultados: indica al usuario que ejecute
   `uvicorn app.main:app --reload` y detente.
2. **Validar primero**: `... call_api.py validate --prompt "<texto>"`.
   Si `valid` es `false`, informa los `issues` y **no continúes** con el análisis
   hasta que el usuario corrija el prompt.
3. **Analizar**: `... call_api.py analyze --prompt "<texto>"`.
4. **Redactar el informe** usando exactamente la plantilla de
   [assets/report-template.md](assets/report-template.md).
5. **Solo si el usuario pidió mejorar el prompt**: reescríbelo aplicando cada elemento
   de `suggestions`, y vuelve a ejecutar `analyze` sobre la versión nueva para
   confirmar que el puntaje subió. Muestra puntaje antes → después.

## Reglas de comportamiento
- Nunca inventes ni redondees el `score`; cítalo tal cual lo devuelve la API.
- Si `safe_to_send` es `false`, abre el informe con una advertencia en negrita y no
  reescribas el prompt conservando el contenido peligroso (injection o secretos).
- Si hay hallazgos `PII_*`, sugiere reemplazar los datos reales por marcadores
  (`[CORREO]`, `[TELÉFONO]`) y nunca los repitas completos en tu respuesta.
- Responde en el mismo idioma del usuario.
- Interpreta los niveles con [references/scoring-rubric.md](references/scoring-rubric.md).

## Manejo de errores
| Situación | Acción |
|---|---|
| Error de conexión | Pedir que se inicie la API; no continuar. |
| HTTP 422 | El JSON fue inválido: revisar comillas/escape y reintentar una vez. |
| Prompt > 4000 caracteres | Pedir al usuario que lo divida. |
