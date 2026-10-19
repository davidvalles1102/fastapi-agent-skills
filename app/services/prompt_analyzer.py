"""Lógica de negocio: análisis y validación de prompts.

No conoce FastAPI ni HTTP: recibe texto y devuelve modelos de dominio. Esto lo
hace reutilizable y fácil de probar de forma aislada.
"""
import re

from app.core.config import Settings
from app.schemas.prompt import AnalysisResponse, Finding, ValidationResponse

# criterio -> (peso, patrón). Los pesos suman 100. Soporta español e inglés.
_CRITERIA: dict[str, tuple[int, re.Pattern[str]]] = {
    "rol": (15, re.compile(
        r"\b(act[úu]a como|eres un[a]?|compórtate como|como un[a]? experto|act as|you are|as an? expert)\b", re.I)),
    "tarea": (25, re.compile(
        r"\b(escribe|redacta|genera|explica|resume|analiza|traduce|crea|lista|compara|calcula|describe|dise[ñn]a|"
        r"write|generate|explain|summari[sz]e|analy[sz]e|translate|create|list|compare|calculate|describe|design)\b", re.I)),
    "contexto": (20, re.compile(
        r"\b(contexto|audiencia|p[úu]blico|estudiantes|dado que|context|audience|background|given that|for a)\b", re.I)),
    "formato": (15, re.compile(
        r"\b(formato|tabla|json|vi[ñn]etas|markdown|p[áa]rrafos?|format|table|bullets?|paragraphs?)\b", re.I)),
    "restricciones": (15, re.compile(
        r"(\b(m[áa]ximo|m[íi]nimo|evita|no incluyas|debe|at most|at least|avoid|must|limit)\b|"
        r"\b\d+\s*(palabras|l[íi]neas|puntos|words|lines|items)\b)", re.I)),
    "ejemplos": (10, re.compile(
        r"\b(ejemplo|por ejemplo|example|for example|e\.g\.)\b", re.I)),
}

_SUGGESTIONS = {
    "rol": "Define un rol para el modelo (p. ej. 'Actúa como profesor de bases de datos').",
    "tarea": "Indica la tarea con un verbo de acción claro (explica, resume, compara...).",
    "contexto": "Añade contexto: audiencia, nivel o situación en la que se usará la respuesta.",
    "formato": "Especifica el formato de salida (lista, tabla, JSON, número de párrafos).",
    "restricciones": "Agrega restricciones medibles (máximo de palabras, qué evitar).",
    "ejemplos": "Incluye un ejemplo breve de la salida esperada.",
}

_INJECTION = re.compile(
    r"(ignora (todas )?las instrucciones|olvida (todo|tus instrucciones)|ignore (all |any )?(previous|prior) instructions|"
    r"disregard (the )?(system|previous)|reveal (the |your )?system prompt|muestra tu prompt de sistema)", re.I)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s-]?)?\d{4}[\s-]?\d{4}(?!\d)")
_SECRET = re.compile(r"(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|api[_-]?key\s*[:=]\s*\S+)", re.I)


class PromptAnalyzer:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @staticmethod
    def _counts(prompt: str) -> tuple[int, int]:
        return len(prompt), len(prompt.split())

    def _risk_findings(self, prompt: str) -> list[Finding]:
        findings: list[Finding] = []
        if _INJECTION.search(prompt):
            findings.append(Finding(code="PROMPT_INJECTION", severity="critical",
                                    message="Se detectó un patrón típico de prompt injection."))
        if _SECRET.search(prompt):
            findings.append(Finding(code="SECRET_LEAK", severity="critical",
                                    message="El prompt parece contener una clave o token secreto."))
        if _EMAIL.search(prompt):
            findings.append(Finding(code="PII_EMAIL", severity="warning",
                                    message="El prompt contiene un correo electrónico."))
        if _PHONE.search(prompt):
            findings.append(Finding(code="PII_PHONE", severity="warning",
                                    message="El prompt parece contener un número telefónico."))
        return findings

    def validate(self, prompt: str) -> ValidationResponse:
        chars, words = self._counts(prompt)
        issues: list[Finding] = []
        stripped = prompt.strip()
        if not stripped:
            issues.append(Finding(code="EMPTY", severity="critical", message="El prompt está vacío."))
        elif len(stripped) < self._settings.min_prompt_chars:
            issues.append(Finding(code="TOO_SHORT", severity="critical",
                                  message=f"Mínimo {self._settings.min_prompt_chars} caracteres."))
        if chars > self._settings.max_prompt_chars:
            issues.append(Finding(code="TOO_LONG", severity="critical",
                                  message=f"Máximo {self._settings.max_prompt_chars} caracteres."))
        issues.extend(self._risk_findings(prompt))
        valid = not any(i.severity == "critical" for i in issues)
        return ValidationResponse(valid=valid, char_count=chars, word_count=words, issues=issues)

    def analyze(self, prompt: str) -> AnalysisResponse:
        chars, words = self._counts(prompt)
        criteria = {name: bool(rx.search(prompt)) for name, (_, rx) in _CRITERIA.items()}
        score = sum(weight for name, (weight, _) in _CRITERIA.items() if criteria[name])

        findings = self._risk_findings(prompt)
        for f in findings:
            score -= 25 if f.severity == "critical" else 10
        score = max(0, min(100, score))

        suggestions = [_SUGGESTIONS[name] for name, ok in criteria.items() if not ok]
        if words < 8:
            suggestions.append("El prompt es muy corto: describe con más detalle lo que necesitas.")

        level = ("deficiente" if score < 40 else "aceptable" if score < 65
                 else "bueno" if score < 85 else "excelente")
        return AnalysisResponse(
            score=score, level=level,
            safe_to_send=not any(f.severity == "critical" for f in findings),
            criteria=criteria, findings=findings, suggestions=suggestions,
            char_count=chars, word_count=words,
        )
