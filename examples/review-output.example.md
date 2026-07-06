# Revisão DocTail

> Exemplo de saída de `/doctail:review examples/api-gap.before.md modo=full`.

## Diagnóstico geral

Documento curto e com bom exemplo de payload, mas **não é executável ponta a ponta**: faltam informações críticas para o leitor concluir a integração sem pedir ajuda — onde obter o `<TOKEN>`, a URL base do endpoint, os valores possíveis de status e como validar a resposta.

## Achados prioritários

| Severidade | Tag | Problema | Ação | Local |
|---|---|---|---|---|
| Crítico | gap | Não explica onde obter o `<TOKEN>` de autenticação | Adicionar seção "Autenticação" com origem do token | `## Criar cobrança` |
| Alto | gap | Endpoint sem URL base (host) — `POST /v1/charges` não é chamável | Documentar a base URL oficial | bloco `http` |
| Alto | gap | "Consultar status" não traz endpoint, método nem valores possíveis de status | Especificar `GET /v1/charges/{id}` e enum de status | `## Consultar status` |
| Alto | success | Falta critério de sucesso: como validar que a cobrança foi paga | Definir status esperado (ex.: `paid`) e verificação | `## Consultar status` |
| Médio | structure | Não há pré-requisitos (credenciais, ambiente sandbox vs. produção) | Adicionar "Pré-requisitos" | topo |
| Baixo | shrink | "Com isso a integração está feita" não agrega | Remover conclusão vazia | `## Pronto` |

## Riscos preservados

- `amount` em **centavos** — mantido explicitamente (erro aqui tem impacto financeiro).
- Campos oficiais `amount`, `currency`, `customer_id` e header `Authorization: Bearer` — preservados sem renomear.

## Lacunas

- Origem do token de autenticação (`gap` crítico).
- URL base da API (`gap`).
- Endpoint, método e enum de status da consulta (`gap`).
- Critério de sucesso do pagamento (`success`).
- Ambiente sandbox vs. produção (`gap`).

## Impacto estimado

- Redução estimada de palavras: -10%
- Problemas de estrutura: 1
- Duplicidades: 0
- Lacunas críticas: 1
- Riscos preservados: 2
