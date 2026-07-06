#!/usr/bin/env python3
"""doctail find-docs — localiza arquivos de documentação em uma árvore de diretórios.

Uso:
    doctail_find_docs.py [path] [--json]

Sem argumento de path, usa o diretório atual. Apenas biblioteca padrão.
"""
import argparse
import json
import os
import sys

# Extensões consideradas documentação.
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".adoc", ".txt"}

# Nomes de arquivo tratados como documentação mesmo sem extensão da lista.
DOC_FILENAMES = {
    "README",
    "README.md",
    "CONTRIBUTING",
    "CONTRIBUTING.md",
    "CHANGELOG",
    "CHANGELOG.md",
}

# Pastas cujo nome sinaliza documentação (usado só para relatório/priorização).
DOC_DIRS = {"docs", "wiki", "playbooks", "sops", "knowledge-base"}

# Diretórios sempre ignorados.
IGNORE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    ".next",
    "coverage",
    "tmp",
}


def is_doc_file(name):
    """Retorna True se o nome do arquivo for documentação."""
    if name in DOC_FILENAMES:
        return True
    _, ext = os.path.splitext(name)
    if ext.lower() in DOC_EXTENSIONS:
        return True
    # README com sufixo de idioma, ex.: README.pt-BR.md já cai na extensão.
    if name.upper().startswith("README"):
        return True
    return False


def find_docs(root):
    """Percorre root e devolve lista ordenada de caminhos de documentação."""
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Poda in-place para não descer em diretórios ignorados.
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for name in filenames:
            if is_doc_file(name):
                results.append(os.path.join(dirpath, name))
    return sorted(results)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="doctail find-docs",
        description="Localiza arquivos de documentação.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Pasta a varrer (padrão: .)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON.")
    args = parser.parse_args(argv)

    root = args.path
    if not os.path.exists(root):
        sys.stderr.write("Caminho não encontrado: %s\n" % root)
        return 1

    if os.path.isfile(root):
        docs = [root] if is_doc_file(os.path.basename(root)) else []
    else:
        docs = find_docs(root)

    if args.json:
        print(json.dumps({"root": root, "count": len(docs), "files": docs}, ensure_ascii=False, indent=2))
    else:
        for path in docs:
            print(path)
        if not docs:
            sys.stderr.write("Nenhum arquivo de documentação encontrado em %s\n" % root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
