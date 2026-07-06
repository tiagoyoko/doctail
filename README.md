<div align="center">

# 📄 DocTail

**Revisor, simplificador e auditor de documentação** para Claude Code.

Um produto da **[Agência Vibe Code](https://agenciavibecode.com)**.

[![Versão](https://img.shields.io/badge/vers%C3%A3o-0.1.0-2563eb)](CHANGELOG.md)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-16a34a)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-7c3aed)](https://claude.com/claude-code)
[![Idioma](https://img.shields.io/badge/idioma-pt--BR-f59e0b)](#)

</div>

---

Plugin autocontido, versionável e testável localmente.

DocTail não é um resumidor genérico. É um **revisor operacional anti-burocracia**, guiado por um único princípio:

> A melhor documentação é a menor documentação que ainda permite ao leitor executar a tarefa corretamente, sem ambiguidade e sem pedir ajuda.

O trabalho do DocTail: cortar excesso, remover repetição, preservar precisão, reorganizar conteúdo, transformar texto confuso em documentação executável, identificar lacunas, proteger informações críticas e padronizar linguagem e estrutura.

## Quando usar

- Documentação **inchada, burocrática ou confusa** que precisa virar executável.
- **Bases de conhecimento** com duplicidade, conflito ou páginas obsoletas.
- Documentação de **processos, CRM, vendas, marketing e automações** que precisa ser operável sem depender do criador original.
- Documentação **técnica** (APIs, comandos, parâmetros) que precisa de precisão e de sinalização de lacunas.
- Revisão de **mudanças de documentação** como se fosse um pull request.

## Estrutura do plugin

```text
doctail/
├── .claude-plugin/
│   └── plugin.json          # manifest do plugin (único arquivo aqui)
├── skills/                  # skills invocáveis /doctail:*
│   ├── review/SKILL.md
│   ├── simplify/SKILL.md
│   ├── audit/SKILL.md
│   ├── diff/SKILL.md
│   └── style/SKILL.md
├── agents/                  # subagents especializados
│   ├── doc-auditor.md       # read-only
│   └── doc-refactorer.md    # edita quando solicitado
├── hooks/
│   └── hooks.json           # PreToolUse (guard) + PostToolUse (alerta)
├── scripts/                 # Python 3, apenas biblioteca padrão
│   ├── doctail_find_docs.py
│   ├── doctail_metrics.py
│   ├── doctail_dedupe.py
│   ├── doctail_hook_guard.py
│   ├── doctail_hook_post_edit.py
│   └── doctail_validate.py
├── bin/
│   └── doctail              # wrapper CLI
├── examples/                # antes/depois e exemplo de saída
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## Comandos disponíveis (CLI)

O binário `bin/doctail` funciona a partir de qualquer diretório:

```bash
doctail find-docs [path] [--json]
doctail metrics   [path] [--json]
doctail dedupe    [path] [--json] [--threshold 0.86]
doctail validate
doctail help
```

## Skills

| Skill | Edita? | Para quê |
|---|---|---|
| `/doctail:review` | Não | Diagnóstico: achados de clareza, excesso, lacunas, duplicidade, risco e estrutura de **um arquivo ou pasta**. |
| `/doctail:simplify` | Sim (com pedido) | Reescreve um **arquivo** longo/burocrático em versão clara e executável, preservando o crítico. |
| `/doctail:audit` | Não | Audita **múltiplos arquivos**: páginas inchadas, duplicadas, lacunas, obsolescência. Relatório priorizado + top 10 ações. |
| `/doctail:diff` | Não | Revisa **mudanças recentes** de documentação como um pull request. |
| `/doctail:style` | Sim (com pedido) | Padroniza forma (títulos, termos, tom, tabelas) **sem alterar significado técnico**. |

Diferença rápida: `review` diagnostica um alvo, `audit` diagnostica uma coleção, `diff` diagnostica um changeset. `simplify` reescreve conteúdo; `style` padroniza a forma sem mexer no conteúdo técnico.

### Exemplos de uso

```text
/doctail:review docs/onboarding.md
/doctail:simplify docs/processo-comercial.md modo=full
/doctail:audit ./docs modo=ultra
/doctail:diff main...HEAD
/doctail:style docs/crm.md
```

Modos (`review`, `simplify`, `audit`): `lite` (conservador), `full` (padrão), `ultra` (mais profundo/agressivo).

## Hooks

- **PreToolUse (`doctail_hook_guard.py`)**: bloqueia comandos Bash destrutivos contra documentação (`rm -rf docs`, `find docs -delete`, `git clean -fd docs`, remoção em massa de `.md/.mdx/.rst/.adoc`, truncamento com `>`). Comandos seguros (`git diff`, `grep`, `ls`, `cat`, scripts Python) passam sem bloqueio.
- **PostToolUse (`doctail_hook_post_edit.py`)**: após editar documentação, imprime um alerta curto quando encontra problemas óbvios (parágrafo > 120 palavras, arquivo > 1500 palavras sem estrutura, sem H1, excesso de termos burocráticos, TODO/FIXME, "atualizar depois", links vazios, cabeçalhos duplicados). Nunca modifica o arquivo e nunca bloqueia.

## Como testar localmente

```bash
claude --plugin-dir ./doctail
```

Depois, dentro do Claude Code:

```text
/doctail:review examples/bloated-intro.before.md
/doctail:simplify examples/crm-automation.before.md modo=full
/doctail:audit ./examples modo=ultra
/doctail:diff main...HEAD
/doctail:style examples/api-gap.before.md
```

Recarregar durante o desenvolvimento:

```text
/reload-plugins
```

## Como validar

```bash
python3 doctail/scripts/doctail_validate.py
claude plugin validate ./doctail --strict
```

E a CLI:

```bash
doctail/bin/doctail help
doctail/bin/doctail metrics ./doctail/examples
```

## Limitações

- **Não substitui revisão humana** — DocTail prioriza e sugere; a decisão final é sua.
- **Não inventa lacunas nem informações.** Onde falta informação, ele marca `gap` em vez de preencher.
- **Não simplifica documentação legal/compliance de forma agressiva** — nesses casos opera em modo conservador, mesmo sob pedido de agressividade, salvo instrução explícita.
- **Os hooks não alteram arquivos automaticamente.** O guard bloqueia; o pós-edição só alerta.
- A detecção de duplicidade (`dedupe`) compara pares de parágrafos e é `O(n²)` no número de parágrafos — em bases muito grandes, rode por subpasta.

## Licença

Distribuído sob a licença [MIT](LICENSE). © 2026 Agência Vibe Code.

---

<div align="center">

Feito com foco em documentação executável pela **[Agência Vibe Code](https://agenciavibecode.com)**.

Dúvidas, sugestões ou uso corporativo: [tiago@agenciavibecode.com](mailto:tiago@agenciavibecode.com)

</div>
