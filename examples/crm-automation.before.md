# Automação CRM

Então basicamente a gente tem uma automação no CRM que quando um lead novo entra ele vai sendo movido pelo funil e aí em algum momento a gente precisa que ele seja atribuído pro vendedor certo, mas isso depende de algumas coisas. Vale ressaltar que é importante destacar que essa automação foi feita faz um tempo e talvez precise atualizar depois.

A ideia é a seguinte: quando o lead chega na etapa de "Qualificado" no pipeline de Vendas, a automação dispara. Ela olha pro campo de região (o campo se chama regiao_comercial no sistema, não confundir com o campo regiao que é do endereço) e aí distribui. Se for Sul ou Sudeste vai pro time A, se for Norte, Nordeste ou Centro-Oeste vai pro time B. Mas atenção que se o campo estiver vazio ele não pode ficar parado, tem que cair numa fila de revisão manual senão o lead se perde e a gente já perdeu negócio assim.

Ah, e tem o webhook que manda pro sistema de e-mail marketing. Isso aqui é meio perigoso porque se disparar duas vezes o cara recebe e-mail duplicado e já teve reclamação. O SLA de primeiro contato é de 2 horas úteis, isso é importante e não pode mudar sem falar com o comercial. Também impacta o relatório de conversão por região, então se mexer no campo regiao_comercial quebra o relatório.

Uma exceção: contas marcadas como "Enterprise" nunca entram nessa automação, elas vão direto pro closer sênior manualmente. Isso é regra.

Lembrando que essa automação depende da integração com o e-mail marketing estar ativa e do webhook estar configurado, senão nada funciona.
