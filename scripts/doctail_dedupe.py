#!/usr/bin/env python3
"""doctail dedupe — detecta duplicidade entre arquivos de documentação.

Uso:
    doctail_dedupe.py [path] [--json] [--threshold 0.86]

Detecta headings repetidos, parágrafos idênticos, parágrafos quase duplicados
(via difflib.SequenceMatcher) e páginas com títulos muito similares.
Apenas biblioteca padrão.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import sys

DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".adoc", ".txt"}
IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build", ".venv", "venv", ".next", "coverage", "tmp",
}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

# Parágrafos com menos palavras que isto são ignorados (ruído).
MIN_PARAGRAPH_WORDS = 8


def collect_files(root):
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


def normalize(text):
    """Colapsa espaços e minúsculas para comparação estável."""
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_headings(text):
    headings = []
    for line in text.splitlines():
        m = HEADING_RE.match(line.strip())
        if m:
            headings.append(m.group(2).strip())
    return headings


def extract_paragraphs(text):
    blocks = re.split(r"\n\s*\n", text)
    paras = []
    for b in blocks:
        b = b.strip()
        if not b or b.startswith("```") or b.startswith("#"):
            continue
        if len(re.findall(r"\S+", b)) >= MIN_PARAGRAPH_WORDS:
            paras.append(b)
    return paras


def first_heading(text):
    """Devolve o primeiro heading do documento (título provável)."""
    hs = extract_headings(text)
    return hs[0] if hs else None


def analyze(files, threshold):
    docs = {}
    for path in files:
        try:
            docs[path] = read_text(path)
        except OSError as exc:
            sys.stderr.write("Erro ao ler %s: %s\n" % (path, exc))

    # Headings repetidos entre arquivos.
    heading_index = {}
    for path, text in docs.items():
        for h in extract_headings(text):
            key = normalize(h)
            heading_index.setdefault(key, []).append(path)
    repeated_headings = [
        {"heading": key, "files": sorted(set(paths))}
        for key, paths in heading_index.items()
        if len(set(paths)) > 1
    ]

    # Parágrafos idênticos (hash) e quase duplicados (SequenceMatcher).
    para_entries = []  # (path, paragraph_text, normalized)
    for path, text in docs.items():
        for para in extract_paragraphs(text):
            para_entries.append((path, para, normalize(para)))

    identical = {}
    for path, para, norm in para_entries:
        digest = hashlib.sha1(norm.encode("utf-8")).hexdigest()
        identical.setdefault(digest, {"sample": para, "files": []})
        identical[digest]["files"].append(path)
    identical_paragraphs = [
        {"sample": v["sample"][:200], "files": sorted(set(v["files"]))}
        for v in identical.values()
        if len(set(v["files"])) > 1 or len(v["files"]) > 1
    ]

    # Quase duplicados: compara pares de parágrafos de arquivos diferentes.
    near_duplicates = []
    n = len(para_entries)
    for i in range(n):
        p1, para1, norm1 = para_entries[i]
        for j in range(i + 1, n):
            p2, para2, norm2 = para_entries[j]
            if p1 == p2:
                continue
            if norm1 == norm2:
                continue  # já contado como idêntico
            ratio = difflib.SequenceMatcher(None, norm1, norm2).ratio()
            if ratio >= threshold:
                near_duplicates.append({
                    "ratio": round(ratio, 3),
                    "file_a": p1,
                    "file_b": p2,
                    "sample_a": para1[:160],
                    "sample_b": para2[:160],
                })

    # Títulos de página muito similares.
    titles = [(path, first_heading(text)) for path, text in docs.items()]
    titles = [(p, t) for p, t in titles if t]
    similar_titles = []
    for i in range(len(titles)):
        pa, ta = titles[i]
        for j in range(i + 1, len(titles)):
            pb, tb = titles[j]
            ratio = difflib.SequenceMatcher(None, normalize(ta), normalize(tb)).ratio()
            if ratio >= threshold:
                similar_titles.append({
                    "ratio": round(ratio, 3),
                    "file_a": pa, "title_a": ta,
                    "file_b": pb, "title_b": tb,
                })

    return {
        "threshold": threshold,
        "repeated_headings": repeated_headings,
        "identical_paragraphs": identical_paragraphs,
        "near_duplicates": near_duplicates,
        "similar_titles": similar_titles,
    }


def render_markdown(result):
    out = ["# Duplicidade DocTail", "", "Threshold: %.2f" % result["threshold"], ""]

    out.append("## Headings repetidos entre arquivos")
    if result["repeated_headings"]:
        for item in result["repeated_headings"]:
            out.append("- **%s** — %s" % (item["heading"], ", ".join(item["files"])))
    else:
        out.append("- Nenhum.")
    out.append("")

    out.append("## Parágrafos idênticos")
    if result["identical_paragraphs"]:
        for item in result["identical_paragraphs"]:
            out.append("- %s… — %s" % (item["sample"], ", ".join(item["files"])))
    else:
        out.append("- Nenhum.")
    out.append("")

    out.append("## Parágrafos quase duplicados")
    if result["near_duplicates"]:
        for item in result["near_duplicates"]:
            out.append("- (%.3f) %s ↔ %s" % (item["ratio"], item["file_a"], item["file_b"]))
    else:
        out.append("- Nenhum.")
    out.append("")

    out.append("## Títulos de página muito similares")
    if result["similar_titles"]:
        for item in result["similar_titles"]:
            out.append("- (%.3f) \"%s\" (%s) ↔ \"%s\" (%s)" % (
                item["ratio"], item["title_a"], item["file_a"], item["title_b"], item["file_b"]))
    else:
        out.append("- Nenhum.")
    out.append("")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="doctail dedupe", description="Detecta duplicidade em docs.")
    parser.add_argument("path", nargs="?", default=".", help="Pasta ou arquivo (padrão: .)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON.")
    parser.add_argument("--threshold", type=float, default=0.86, help="Similaridade mínima (0-1).")
    args = parser.parse_args(argv)

    if not os.path.exists(args.path):
        sys.stderr.write("Caminho não encontrado: %s\n" % args.path)
        return 1
    if not 0 < args.threshold <= 1:
        sys.stderr.write("Threshold deve estar em (0, 1].\n")
        return 1

    files = collect_files(args.path)
    result = analyze(files, args.threshold)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
