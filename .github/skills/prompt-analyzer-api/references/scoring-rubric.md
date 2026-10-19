# Cómo interpretar el puntaje

La API evalúa seis criterios. Los pesos suman 100.

| Criterio | Peso | Qué busca |
|---|---|---|
| tarea | 25 | Verbo de acción claro (explica, resume, compara...) |
| contexto | 20 | Audiencia, nivel o situación de uso |
| rol | 15 | "Actúa como...", "Eres un..." |
| formato | 15 | Lista, tabla, JSON, número de párrafos |
| restricciones | 15 | Límites medibles o cosas a evitar |
| ejemplos | 10 | Un ejemplo de la salida esperada |

## Penalizaciones por riesgo
- Hallazgo **critical** (`PROMPT_INJECTION`, `SECRET_LEAK`): −25 cada uno.
- Hallazgo **warning** (`PII_EMAIL`, `PII_PHONE`): −10 cada uno.

## Niveles
| Puntaje | Nivel | Qué decirle al usuario |
|---|---|---|
| 0–39 | deficiente | Faltan elementos básicos; reescribir. |
| 40–64 | aceptable | Funciona, pero con resultados poco predecibles. |
| 65–84 | bueno | Ajustes menores. |
| 85–100 | excelente | Listo para usar. |

## Límites conocidos (decirlo si el usuario lo pregunta)
El análisis es heurístico (palabras clave): mide **estructura**, no la calidad
de las ideas. Un prompt puede puntuar 100 y aun así pedir algo ambiguo.
