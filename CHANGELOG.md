# Changelog

Todas as mudanças relevantes deste plugin são documentadas aqui. O formato segue
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o versionamento
segue [SemVer](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-07-06

### Adicionado

- Manifest do plugin (`.claude-plugin/plugin.json`).
- Skills: `review`, `simplify`, `audit`, `diff`, `style`.
- Subagents: `doc-auditor` (read-only) e `doc-refactorer` (edita sob pedido).
- Hooks: `PreToolUse` (guard contra comandos destrutivos) e `PostToolUse`
  (alerta pós-edição de documentação).
- Scripts (Python 3, biblioteca padrão): `doctail_find_docs`, `doctail_metrics`,
  `doctail_dedupe`, `doctail_hook_guard`, `doctail_hook_post_edit`,
  `doctail_validate`.
- Wrapper CLI `bin/doctail` com `find-docs`, `metrics`, `dedupe`, `validate`, `help`.
- Exemplos antes/depois e exemplo de saída de review.
- Documentação de uso (`README.md`) e licença MIT.
