#!/usr/bin/env python3
"""doctail_hook_post_edit.py — hook PostToolUse.

Após Write/Edit/MultiEdit em documentação, calcula métricas leves e imprime
um alerta curto quando encontra problemas óbvios. Nunca modifica o arquivo,
nunca bloqueia a edição, sempre sai com código 0.
"""
import json
import os
import re
import sys

DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".adoc", ".txt"}
DOC_DIRS = {"docs", "playbooks", "sops", "wiki", "knowledge-base"}

LONG_PARAGRAPH_WORDS = 120
LARGE_FILE_WORDS = 1500

BUREAUCRATIC_TERMS = [
    "é importante destacar que", "vale ressaltar que", "de maneira adequada",
    "de forma assertiva", "visando", "no que tange", "conforme mencionado anteriormente",
    "faz-se necessário", "em virtude de", "com o objetivo de",
]
STALE_PHRASES = ["atualizar depois", "em breve"]
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
EMPTY_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*\)")


def read_stdin_json():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {}


def extract_file_path(data):
    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    if isinstance(tool_input, dict):
        for key in ("file_path", "filePath", "path"):
            if tool_input.get(key):
                return tool_input[key]
    tool_response = data.get("tool_response") or data.get("toolResponse") or {}
    if isinstance(tool_response, dict):
        for key in ("file_path", "filePath", "path"):
            if tool_response.get(key):
                return tool_response[key]
    return None


def is_doc(path):
    name = os.path.basename(path)
    _, ext = os.path.splitext(name)
    if ext.lower() in DOC_EXTENSIONS:
        return True
    if name.upper().startswith("README"):
        return True
    parts = {p.lower() for p in path.replace("\\", "/").split("/")}
    return bool(parts & DOC_DIRS)


def split_paragraphs(text):
    blocks = re.split(r"\n\s*\n", text)
    return [b.strip() for b in blocks if b.strip()]


def check(text):
    problems = []
    lines = text.splitlines()
    words = re.findall(r"\S+", text)

    headings = []
    for line in lines:
        m = HEADING_RE.match(line.strip())
        if m:
            headings.append((len(m.group(1)), m.group(2).strip().lower()))

    if not any(level == 1 for level, _ in headings):
        problems.append("sem título H1")

    if len(words) > LARGE_FILE_WORDS and len(headings) < 3:
        problems.append("arquivo grande (>%d palavras) sem estrutura clara" % LARGE_FILE_WORDS)

    long_paras = 0
    for para in split_paragraphs(text):
        if para.startswith("```"):
            continue
        if len(re.findall(r"\S+", para)) > LONG_PARAGRAPH_WORDS:
            long_paras += 1
    if long_paras:
        problems.append("%d parágrafo(s) acima de %d palavras" % (long_paras, LONG_PARAGRAPH_WORDS))

    text_lower = text.lower()
    bureaucratic = sum(text_lower.count(t) for t in BUREAUCRATIC_TERMS)
    if bureaucratic >= 3:
        problems.append("muitos termos burocráticos (%d)" % bureaucratic)

    todo_fixme = len(re.findall(r"\b(TODO|FIXME)\b", text))
    if todo_fixme:
        problems.append("%d marcador(es) TODO/FIXME" % todo_fixme)

    stale = sum(text_lower.count(p) for p in STALE_PHRASES)
    if stale:
        problems.append("frases de conteúdo pendente (\"atualizar depois\"/\"em breve\")")

    if EMPTY_LINK_RE.search(text):
        problems.append("links markdown vazios")

    seen = {}
    for _, title in headings:
        seen[title] = seen.get(title, 0) + 1
    dup = [t for t, c in seen.items() if c > 1]
    if dup:
        problems.append("cabeçalhos duplicados (%d)" % len(dup))

    return problems


def main():
    data = read_stdin_json()
    path = extract_file_path(data)
    if not path or not is_doc(path):
        return 0
    if not os.path.isfile(path):
        return 0

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return 0

    problems = check(text)
    if problems:
        sys.stderr.write("[DocTail] Alerta em %s:\n" % os.path.basename(path))
        for p in problems:
            sys.stderr.write("  - %s\n" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
