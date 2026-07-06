#!/usr/bin/env python3
"""doctail metrics — calcula métricas de qualidade de documentação.

Uso:
    doctail_metrics.py [path] [--json]

path pode ser arquivo ou pasta. Sem argumento, usa o diretório atual.
Apenas biblioteca padrão.
"""
import argparse
import json
import os
import re
import sys

DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".adoc", ".txt"}
IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build", ".venv", "venv", ".next", "coverage", "tmp",
}

# Termos burocráticos que sinalizam texto inflado (case-insensitive).
BUREAUCRATIC_TERMS = [
    "é importante destacar que",
    "vale ressaltar que",
    "de maneira adequada",
    "de forma assertiva",
    "visando",
    "no que tange",
    "conforme mencionado anteriormente",
    "faz-se necessário",
    "em virtude de",
    "com o objetivo de",
]

# Sinais de conteúdo possivelmente obsoleto.
STALE_SIGNALS = [
    "em breve",
    "a definir",
    "atualizar depois",
    "TODO",
    "FIXME",
    "temporário",
    "legado",
    "deprecated",
    "obsoleto",
]

# Pistas de que o documento descreve um procedimento (passo a passo).
PROCEDURE_HINTS = [
    "passo a passo", "passo 1", "1.", "etapa", "execute", "rode", "clique",
    "configure", "instale", "procedimento",
]

# Cabeçalhos que indicam presença de pré-requisitos.
PREREQ_HINTS = ["pré-requisito", "pre-requisito", "prerequisito", "requisitos", "antes de começar"]

# Cabeçalhos que indicam critério de sucesso / validação final.
SUCCESS_HINTS = [
    "critério de sucesso", "criterio de sucesso", "validação", "validacao",
    "resultado esperado", "como validar", "verificação final", "verificacao final",
    "definition of done", "critério de conclusão", "criterio de conclusao",
]

LONG_PARAGRAPH_WORDS = 120
LARGE_FILE_WORDS = 1500
WORDS_PER_MINUTE = 200

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def count_occurrences(text_lower, terms):
    """Conta ocorrências totais de uma lista de termos em texto minúsculo."""
    total = 0
    hits = {}
    for term in terms:
        c = text_lower.count(term.lower())
        if c:
            hits[term] = c
            total += c
    return total, hits


def split_paragraphs(text):
    """Divide o texto em parágrafos por linhas em branco."""
    blocks = re.split(r"\n\s*\n", text)
    return [b.strip() for b in blocks if b.strip()]


def analyze_text(text):
    """Devolve dict de métricas de um único conteúdo de documento."""
    lines = text.splitlines()
    words = re.findall(r"\S+", text)
    word_count = len(words)
    line_count = len(lines)
    reading_minutes = round(word_count / WORDS_PER_MINUTE, 1) if word_count else 0.0

    headings = []
    for line in lines:
        m = HEADING_RE.match(line.strip())
        if m:
            headings.append((len(m.group(1)), m.group(2).strip()))

    heading_titles = [h[1] for h in headings]
    seen = {}
    duplicate_headings = []
    for title in heading_titles:
        key = title.lower()
        seen[key] = seen.get(key, 0) + 1
    for key, c in seen.items():
        if c > 1:
            duplicate_headings.append({"heading": key, "count": c})

    has_h1 = any(level == 1 for level, _ in headings)

    long_paragraphs = 0
    for para in split_paragraphs(text):
        # Ignora blocos de código para não inflar contagem de palavras.
        if para.startswith("```"):
            continue
        if len(re.findall(r"\S+", para)) > LONG_PARAGRAPH_WORDS:
            long_paragraphs += 1

    text_lower = text.lower()
    bureaucratic_total, bureaucratic_hits = count_occurrences(text_lower, BUREAUCRATIC_TERMS)

    # TODO/FIXME são case-sensitive por convenção; demais sinais case-insensitive.
    todo_fixme = len(re.findall(r"\b(TODO|FIXME)\b", text))
    stale_total, stale_hits = count_occurrences(text_lower, STALE_SIGNALS)

    looks_like_procedure = any(h in text_lower for h in PROCEDURE_HINTS)
    has_prereq = any(h in text_lower for h in PREREQ_HINTS)
    has_success = any(h in text_lower for h in SUCCESS_HINTS)

    missing_prereq = looks_like_procedure and not has_prereq
    missing_success = looks_like_procedure and not has_success

    large_file = word_count > LARGE_FILE_WORDS
    unstructured_large = large_file and len(headings) < 3

    return {
        "words": word_count,
        "lines": line_count,
        "reading_minutes": reading_minutes,
        "headings": len(headings),
        "duplicate_headings": duplicate_headings,
        "long_paragraphs": long_paragraphs,
        "bureaucratic_terms": bureaucratic_total,
        "bureaucratic_hits": bureaucratic_hits,
        "todo_fixme": todo_fixme,
        "stale_signals": stale_total,
        "stale_hits": stale_hits,
        "has_h1": has_h1,
        "missing_h1": not has_h1,
        "looks_like_procedure": looks_like_procedure,
        "missing_prereq": missing_prereq,
        "missing_success": missing_success,
        "large_file": large_file,
        "unstructured_large": unstructured_large,
    }


def collect_files(root):
    """Lista arquivos de documentação em um path (arquivo ou pasta)."""
    if os.path.isfile(root):
        return [root]
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for name in filenames:
            _, ext = os.path.splitext(name)
            if ext.lower() in DOC_EXTENSIONS or name.upper().startswith("README"):
                files.append(os.path.join(dirpath, name))
    return sorted(files)


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def render_markdown(reports):
    """Formata os relatórios em markdown."""
    out = ["# Métricas DocTail", ""]
    for rep in reports:
        m = rep["metrics"]
        out.append("## %s" % rep["file"])
        out.append("")
        out.append("- Palavras: %d" % m["words"])
        out.append("- Linhas: %d" % m["lines"])
        out.append("- Tempo estimado de leitura: %s min" % m["reading_minutes"])
        out.append("- Headings: %d" % m["headings"])
        out.append("- Headings duplicados: %d" % len(m["duplicate_headings"]))
        out.append("- Parágrafos longos (>%d palavras): %d" % (LONG_PARAGRAPH_WORDS, m["long_paragraphs"]))
        out.append("- Termos burocráticos: %d" % m["bureaucratic_terms"])
        out.append("- TODO/FIXME: %d" % m["todo_fixme"])
        out.append("- Sinais de obsolescência: %d" % m["stale_signals"])
        flags = []
        if m["missing_h1"]:
            flags.append("sem H1")
        if m["missing_prereq"]:
            flags.append("procedimento sem pré-requisitos")
        if m["missing_success"]:
            flags.append("passo a passo sem critério de sucesso")
        if m["unstructured_large"]:
            flags.append("arquivo grande sem estrutura")
        if flags:
            out.append("- Alertas: %s" % "; ".join(flags))
        out.append("")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="doctail metrics", description="Métricas de documentação.")
    parser.add_argument("path", nargs="?", default=".", help="Arquivo ou pasta (padrão: .)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON.")
    args = parser.parse_args(argv)

    if not os.path.exists(args.path):
        sys.stderr.write("Caminho não encontrado: %s\n" % args.path)
        return 1

    files = collect_files(args.path)
    reports = []
    for path in files:
        try:
            metrics = analyze_text(read_text(path))
        except OSError as exc:
            sys.stderr.write("Erro ao ler %s: %s\n" % (path, exc))
            continue
        reports.append({"file": path, "metrics": metrics})

    if args.json:
        print(json.dumps({"path": args.path, "reports": reports}, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(reports))
    return 0


if __name__ == "__main__":
    sys.exit(main())
