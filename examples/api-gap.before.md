# Integração com a API de Pagamentos

Esta página descreve como integrar com a API de Pagamentos para criar uma cobrança.

## Criar cobrança

Faça uma requisição `POST` para o endpoint de criação de cobrança enviando o valor e o cliente.

```http
POST /v1/charges
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "amount": 1990,
  "currency": "BRL",
  "customer_id": "cus_123"
}
```

O `amount` é em centavos. A resposta traz o `id` da cobrança.

## Consultar status

Depois é só consultar o status da cobrança para saber se foi paga.

## Pronto

Com isso a integração está feita.
