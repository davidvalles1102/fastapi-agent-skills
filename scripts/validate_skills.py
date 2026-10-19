#!/usr/bin/env python3
"""Valida que cada skill de .github/skills/ cumpla el estándar Agent Skills.

Reglas comprobadas:
  * Existe SKILL.md con frontmatter YAML delimitado por ---
  * `name`: minúsculas/números/guiones, <= 64 caracteres, igual al nombre de la carpeta
  * `description`: obligatoria, no vacía, <= 1024 caracteres
  * Los enlaces relativos del cuerpo apuntan a archivos que existen
Solo usa la librería estándar (sin PyYAML).
"""
import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".github" / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)


def parse_top_level(front: str) -> dict[str, str]:
    data = {}
    for line in front.splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)  # solo claves sin indentación
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data


def check_skill(folder: Path) -> list[str]:
    errors: list[str] = []
    skill_md = folder / "SKILL.md"
    if not skill_md.is_file():
        return [f"{folder.name}: falta SKILL.md"]
    match = FRONT_RE.match(skill_md.read_text(encoding="utf-8"))
    if not match:
        return [f"{folder.name}: frontmatter YAML ausente o mal delimitado"]
    meta, body = parse_top_level(match.group(1)), match.group(2)

    name = meta.get("name", "")
    if not name:
        errors.append("falta `name`")
    else:
        if not NAME_RE.match(name) or len(name) > 64:
            errors.append(f"`name` inválido: {name!r}")
        if name != folder.name:
            errors.append(f"`name` ({name}) debe coincidir con la carpeta ({folder.name})")
    desc = meta.get("description", "")
    if not desc:
        errors.append("falta `description`")
    elif len(desc) > 1024:
        errors.append(f"`description` excede 1024 caracteres ({len(desc)})")
    if len(body.strip()) < 200:
        errors.append("el cuerpo de instrucciones es demasiado corto")
    for rel in re.findall(r"\]\(((?!http)[^)#]+)\)", body):
        if not (folder / rel).exists():
            errors.append(f"enlace roto: {rel}")
    return [f"{folder.name}: {e}" for e in errors]


def main() -> int:
    folders = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    if not folders:
        print("No se encontraron skills.")
        return 1
    all_errors = [e for f in folders for e in check_skill(f)]
    for f in folders:
        status = "FALLA" if any(e.startswith(f.name + ":") for e in all_errors) else "OK"
        print(f"[{status}] {f.name}")
    for e in all_errors:
        print("  -", e)
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
