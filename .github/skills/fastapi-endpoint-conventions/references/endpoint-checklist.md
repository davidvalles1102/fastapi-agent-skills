# Checklist de revisión de un endpoint

- [ ] La función de ruta no contiene lógica de negocio.
- [ ] Hay `response_model`, `summary` y `description`.
- [ ] El servicio no importa `fastapi`.
- [ ] Ningún valor "mágico": todo configurable vive en `Settings`.
- [ ] Tests: caso feliz, caso de error y 422.
- [ ] `pytest` y `scripts/validate_skills.py` pasan.
- [ ] README actualizado.
