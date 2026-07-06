#!/usr/bin/env python3
"""doctail validate — valida a estrutura do plugin DocTail.

Checa arquivos obrigatórios, valida o JSON do manifest e dos hooks, confere
shebang nos scripts e a presença do bin. Sai 0 se ok, 1 se houver erro.
Apenas biblioteca padrão.
"""
import json
import os
import sys

# Raiz do plugin = pai da pasta scripts/ onde este arquivo vive.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(SCRIPT_DIR)

REQUIRED_FILES = [
    ".claude-plugin/plugin.json",
    "hooks/hooks.json",
    "bin/doctail",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "skills/review/SKILL.md",
    "skills/simplify/SKILL.md",
    "skills/audit/SKILL.md",
    "skills/diff/SKILL.md",
    "skills/style/SKILL.md",
    "agents/doc-auditor.md",
    "agents/doc-refactorer.md",
    "scripts/doctail_find_docs.py",
    "scripts/doctail_metrics.py",
    "scripts/doctail_dedupe.py",
    "scripts/doctail_hook_guard.py",
    "scripts/doctail_hook_post_edit.py",
    "scripts/doctail_validate.py",
]

SCRIPTS_NEED_SHEBANG = [
    "scripts/doctail_find_docs.py",
    "scripts/doctail_metrics.py",
    "scripts/doctail_dedupe.py",
    "scripts/doctail_hook_guard.py",
    "scripts/doctail_hook_post_edit.py",
    "scripts/doctail_validate.py",
    "bin/doctail",
]

REQUIRED_PLUGIN_KEYS = ["name", "version", "description"]


def rel(path):
    return os.path.join(PLUGIN_ROOT, path)


def check_required_files(errors, oks):
    for f in REQUIRED_FILES:
        if os.path.isfile(rel(f)):
            oks.append("arquivo presente: %s" % f)
        else:
            errors.append("arquivo obrigatório ausente: %s" % f)


def check_json(path, required_keys, errors, oks):
    full = rel(path)
    if not os.path.isfile(full):
        errors.append("JSON ausente: %s" % path)
        return None
    try:
        with open(full, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (ValueError, OSError) as exc:
        errors.append("JSON inválido em %s: %s" % (path, exc))
        return None
    oks.append("JSON válido: %s" % path)
    for key in required_keys:
        if key not in data:
            errors.append("chave obrigatória ausente em %s: %s" % (path, key))
    return data


def check_hooks_json(errors, oks):
    data = check_json("hooks/hooks.json", [], errors, oks)
    if data is None:
        return
    hooks = data.get("hooks", {})
    for event in ("PreToolUse", "PostToolUse"):
        if event not in hooks:
            errors.append("hooks.json sem evento %s" % event)
        else:
            oks.append("hook configurado: %s" % event)


def check_shebangs(errors, oks):
    for f in SCRIPTS_NEED_SHEBANG:
        full = rel(f)
        if not os.path.isfile(full):
            errors.append("script ausente (shebang): %s" % f)
            continue
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as fh:
                first = fh.readline()
        except OSError as exc:
            errors.append("erro lendo %s: %s" % (f, exc))
            continue
        if first.startswith("#!"):
            oks.append("shebang ok: %s" % f)
        else:
            errors.append("sem shebang: %s" % f)


def check_executable(warnings, oks):
    for f in SCRIPTS_NEED_SHEBANG:
        full = rel(f)
        if os.path.isfile(full) and os.access(full, os.X_OK):
            oks.append("executável: %s" % f)
        elif os.path.isfile(full):
            warnings.append("sem permissão de execução (rode chmod +x): %s" % f)


def main():
    errors = []
    warnings = []
    oks = []

    check_required_files(errors, oks)
    check_json(".claude-plugin/plugin.json", REQUIRED_PLUGIN_KEYS, errors, oks)
    check_hooks_json(errors, oks)
    check_shebangs(errors, oks)
    check_executable(warnings, oks)

    print("# Validação do plugin DocTail")
    print("")
    print("Raiz: %s" % PLUGIN_ROOT)
    print("")
    print("## OK (%d)" % len(oks))
    for o in oks:
        print("  ✔ %s" % o)
    if warnings:
        print("")
        print("## Avisos (%d)" % len(warnings))
        for w in warnings:
            print("  ⚠ %s" % w)
    print("")
    if errors:
        print("## Erros (%d)" % len(errors))
        for e in errors:
            print("  x %s" % e)
        print("")
        print("Resultado: FALHOU")
        return 1
    print("## Erros (0)")
    print("")
    print("Resultado: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
