#!/usr/bin/env python3
"""doctail_hook_guard.py — hook PreToolUse.

Bloqueia comandos Bash destrutivos contra arquivos de documentação.
Lê o JSON do hook no stdin, decide, e imprime JSON de decisão quando bloqueia.
Sai com código 0 sempre (a decisão vai no JSON, não no exit code).
Não depende de jq nem de bibliotecas externas.
"""
import json
import re
import sys

EVENT = "PreToolUse"

# Padrões destrutivos contra documentação. Cada tupla: (regex, motivo).
DESTRUCTIVE_PATTERNS = [
    (r"\brm\s+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r|-r\s+-f|-f\s+-r)\b.*\b(docs?|wiki|playbooks?|sops?|knowledge-base)\b",
     "rm recursivo/forçado contra pasta de documentação"),
    (r"\brm\s+-[a-z]*\s+.*\.(md|mdx|rst|adoc)\b.*\*",
     "remoção em massa de arquivos de documentação"),
    (r"\brm\b(?:(?!\|).)*\*\.(md|mdx|rst|adoc)\b",
     "remoção com curinga de arquivos de documentação"),
    (r"\bfind\b.*\b(docs?|wiki|playbooks?|sops?|knowledge-base)\b.*-delete\b",
     "find ... -delete sobre documentação"),
    (r"\bfind\b.*-name\s+['\"]?\*\.(md|mdx|rst|adoc).*-delete\b",
     "find -name '*.md' -delete"),
    (r"\bgit\s+clean\s+-[a-z]*f[a-z]*d?\b.*\b(docs?|wiki|playbooks?|sops?|knowledge-base)\b",
     "git clean forçado sobre documentação"),
    (r">\s*[^>|&\s]+\.(md|mdx|rst|adoc)\b",
     "truncamento de arquivo de documentação com redirecionamento '>'"),
    (r"\btruncate\b.*\.(md|mdx|rst|adoc)\b",
     "truncate sobre arquivo de documentação"),
]

COMPILED = [(re.compile(p, re.IGNORECASE), reason) for p, reason in DESTRUCTIVE_PATTERNS]


def read_stdin_json():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {}


def strip_redirect_from_git(command):
    """Evita falso-positivo: 'git diff > out.md' não deve disparar '>'.

    Não há caso legítimo de truncar documentação com '>', mas escrever a saída
    de um comando de leitura para um .md é comum. Só o '>' isolado é ambíguo;
    mantemos o bloqueio, pois o guard é conservador por design.
    """
    return command


def find_block_reason(command):
    if not command:
        return None
    for regex, reason in COMPILED:
        if regex.search(command):
            return reason
    return None


def deny(reason):
    payload = {
        "hookSpecificOutput": {
            "hookEventName": EVENT,
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "DocTail bloqueou um comando destrutivo contra arquivos de "
                "documentação. Motivo: %s." % reason
            ),
        }
    }
    print(json.dumps(payload, ensure_ascii=False))


def main():
    data = read_stdin_json()
    tool_name = data.get("tool_name") or data.get("toolName")
    if tool_name != "Bash":
        return 0

    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""

    reason = find_block_reason(command)
    if reason:
        deny(reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
