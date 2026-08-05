# Decisão: Serverless completo (sem EC2, sem RDS)

## Contexto
A v1 do projeto usava EC2 (dashboard, stateful) e RDS (armazenamento
relacional). Ambos são recursos "always-on": cobram por hora rodando,
independente de uso. Um projeto anterior gerou custo inesperado por
recurso esquecido ligado — risco incompatível com um projeto de estudo
sem orçamento para erro.

## Decisão
Substituir EC2 por Lambda (consulta da fila) e RDS por S3 (armazenamento
de tickets como JSON). Todo o sistema passa a ser pay-per-uso: sem
requisição, custo é zero, garantido — não depende de lembrar de desligar
nada.

## Trade-off assumido
- Perdido: estado de sessão no dashboard (ex: filtros persistentes entre
  cliques, sem precisar re-buscar tudo).
- Perdido: consultas relacionais complexas que RDS ofereceria (joins,
  agregações via SQL).
- Ganho: custo zero garantido, escala automática de zero, superfície de
  operação menor (nada para monitorar "ligado").

Para o volume e a complexidade deste projeto (fila de tickets, filtro
simples por status/urgência), o trade-off compensa. Se o sistema
crescesse para volume alto ou precisasse de queries relacionais
complexas, RDS voltaria a fazer sentido — mas aí o orçamento também
mudaria de escopo (projeto de produção, não de portfólio de estudo).

## Custo esperado
Budget de $5/mês, alarme em 80%. Free tier cobre 1M invocações Lambda/mês
e 5GB de S3 — volume de teste deve manter o gasto em $0.

## Decisão: classificação por regras, não por LLM em produção

A classificação de tickets usa correspondência de palavras-chave
(`src/ingestao/classificador.py`), não uma chamada de API a um LLM.

Motivo: a Anthropic API é paga por token e não está coberta pelo free
tier da AWS — manter esse custo ativo era incompatível com o orçamento
zero deste projeto de portfólio.

A função `classificar_ticket(texto) -> dict` mantém a mesma assinatura
que uma implementação baseada em LLM teria. Isso significa que o
restante do sistema (handler, S3, dashboard) não precisa mudar caso o
classificador seja trocado por uma chamada real de API no futuro —
a decisão de custo está isolada num único módulo.

Limitação assumida: correspondência por palavra-chave não entende
contexto, negação ou ambiguidade. Um ticket como "não quero mais
reclamar, só um elogio rápido" seria mal classificado. Para um projeto
de produção real, essa limitação justificaria a migração para um LLM,
com o custo sendo avaliado contra o volume real de tickets.

## Problemas encontrados durante a implementação

Durante o desenvolvimento, dois tipos de erro se repetiram e vale
documentar como parte do aprendizado real do projeto:

1. **Escaping de JSON no PowerShell.** Passar JSON inline como
   argumento para `curl.exe` ou `aws` CLI no Windows PowerShell corrompe
   aspas internas de forma inconsistente. Solução adotada: sempre
   escrever o payload em um arquivo `.json` e referenciar via
   `file://caminho`, nunca inline.

2. **Encoding UTF-8 em requisições PowerShell.** `Invoke-RestMethod`
   não força UTF-8 por padrão ao montar o corpo da requisição a partir
   de `ConvertTo-Json`, corrompendo acentos. Solução: converter o corpo
   explicitamente com `[System.Text.Encoding]::UTF8.GetBytes()` antes
   de enviar.

3. **Corrida entre `update_function_code` e
   `update_function_configuration`.** A API da Lambda rejeita a segunda
   chamada se disparada logo após a primeira, pois a atualização do
   código ainda está em progresso. Solução: usar
   `waiter.wait(FunctionName=...)` entre as duas chamadas.

Nenhum desses problemas estava no código da aplicação em si — todos
vieram da camada de teste/cliente local (PowerShell) ou de timing entre
chamadas de infraestrutura, o que reforça a importância de isolar,
via logs estruturados, se uma falha está no sistema ou na forma de
testá-lo.