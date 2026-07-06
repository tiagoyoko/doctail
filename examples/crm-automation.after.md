# Automação de distribuição de leads (pipeline de Vendas)

## Objetivo

Atribuir automaticamente cada lead qualificado ao time comercial correto, por região, garantindo primeiro contato dentro do SLA.

## Quando usar

Dispara automaticamente quando um lead entra na etapa **Qualificado** do pipeline **Vendas**.

## Pré-requisitos

- [ ] Integração com o sistema de e-mail marketing **ativa**.
- [ ] Webhook de e-mail marketing **configurado**.

## Campos envolvidos

| Campo | Sistema | Observação |
|---|---|---|
| `regiao_comercial` | CRM | Base da distribuição. **Não confundir** com `regiao` (endereço). |

> ⚠️ **Risco de relatório:** alterar `regiao_comercial` quebra o relatório de conversão por região.

## Gatilho

Lead atinge a etapa **Qualificado** no pipeline **Vendas**.

## Regra de distribuição

| Valor de `regiao_comercial` | Destino |
|---|---|
| Sul, Sudeste | Time A |
| Norte, Nordeste, Centro-Oeste | Time B |
| Vazio | Fila de **revisão manual** (nunca deixar o lead parado) |

## Exceções

- Contas marcadas como **Enterprise** não entram na automação: vão direto ao **closer sênior**, manualmente.

## Validação final

- [ ] Lead atribuído ao time correto (ou enviado à fila de revisão manual).
- [ ] Primeiro contato registrado dentro do **SLA de 2 horas úteis**.
- [ ] E-mail de marketing disparado **uma única vez**.

## Riscos

- ⚠️ **E-mail duplicado:** disparo duplo do webhook gera e-mail repetido ao lead (já houve reclamação). Garanta idempotência.
- ⚠️ **Perda de lead:** campo `regiao_comercial` vazio sem fila de revisão faz o lead se perder.
- ⚠️ **SLA fixo:** o SLA de primeiro contato de **2 horas úteis** não pode ser alterado sem aprovação do comercial.
- ⚠️ **Dependências:** a automação exige a integração de e-mail marketing ativa e o webhook configurado.
