#!/usr/bin/env python3
"""Cliente mínimo (solo librería estándar) para la API Prompt Analyzer.

Uso:
  python call_api.py health
  python call_api.py validate --prompt "texto"
  python call_api.py analyze  --prompt "texto"
  echo "texto" | python call_api.py analyze          # lee de stdin

Códigos de salida: 0 OK · 1 error HTTP · 2 API inalcanzable · 3 uso incorrecto.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("PROMPT_API_URL", "http://127.0.0.1:8000").rstrip("/")
PREFIX = "/api/v1/prompts"


def request(method: str, path: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        f"{BASE_URL}{path}", data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("command", choices=["health", "validate", "analyze"])
    parser.add_argument("--prompt", help="Texto del prompt (si se omite, se lee de stdin).")
    args = parser.parse_args()

    try:
        if args.command == "health":
            result = request("GET", "/health")
        else:
            prompt = args.prompt if args.prompt is not None else sys.stdin.read().strip()
            if not prompt:
                print("Error: no se recibió ningún prompt.", file=sys.stderr)
                return 3
            result = request("POST", f"{PREFIX}/{args.command}", {"prompt": prompt})
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        print(f"Error HTTP {exc.code}: {detail}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"API inalcanzable en {BASE_URL}: {exc.reason}. "
              "Inicia la API con: uvicorn app.main:app --reload", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
