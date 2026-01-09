
## Olá :)

## ⚠️ Importante:

## Nenhuma dessas mudanças altera o modelo de dados nem quebra integrações existentes.
## Os campos continuam os mesmos , apenas o conteúdo gerado ficou mais coerente.


Atualizações do Simulador (Aluno 6)

Este módulo continua sendo responsável por gerar dados simulados para consumo dos demais componentes do projeto (processadores, diagnósticos e geração de relatórios).

As mudanças abaixo não alteram a estrutura do banco nem os campos existentes, apenas melhoram a qualidade dos dados gerados e adicionam novas formas de consumo.


## Geração de dados mais realistas

Antes, o campo sintomas era preenchido com sintomas mais genéricos.
Agora, os sintomas são gerados de forma aleatória, porém coerente, simulando descrições clínicas simples e realistas mais coerentes com a realidade das lesões mamárias investigadas

Isso melhora:

a leitura humana dos dados

o consumo por outros módulos

a geração de relatórios e arquivos de treino

Importante: os nomes dos campos não mudaram, apenas o conteúdo.


## Diagnóstico fake mais coerente

O campo diagnostico_fake continua existindo, pois já está sendo utilizado por outros módulos do projeto.

A diferença é que agora ele é gerado de forma mais consistente com os sintomas, reduzindo combinações incoerentes (ex: paciente assintomática com diagnóstico grave).

Isso não quebra nenhuma integração existente.


## Novo endpoint: geração de lote

Foi adicionado um endpoint para gerar 10 simulações de uma vez.

Isso facilita testes, carga de dados e integração com outros módulos.

GET /simulador/gerar_lote/


Exemplo em ambiente local:

http://127.0.0.1:8000/simulador/gerar_lote/


## Exportação em ARFF

Também foi adicionado um endpoint que gera um arquivo .arff automaticamente, pronto para uso em ferramentas de machine learning (como WEKA).

Ao acessar a rota, o navegador faz o download do arquivo.

GET /simulador/lote_arff/


Exemplo em ambiente local:

http://127.0.0.1:8000/simulador/lote_arff/





## RESUMO DE TODAS AS ROTAS DA API DO SIMULADOR 




# Gerar uma simulação fake (1 registro)

Cria uma simulação fake, salva no banco e retorna os dados em JSON.

GET /simulador/gerar/


Exemplo em ambiente local:

http://127.0.0.1:8000/simulador/gerar/

# Listar todas as simulações

Retorna uma lista com todas as simulações já geradas e salvas no banco.

GET /simulador/listar/


Exemplo em ambiente local:

http://127.0.0.1:8000/simulador/listar/

# Detalhar uma simulação específica

Retorna os dados completos de uma simulação específica, identificada pelo ID.

GET /simulador/detalhar/<id>/


Exemplo em ambiente local:

http://127.0.0.1:8000/simulador/detalhar/46/

# Gerar lote de simulações (10 registros)

Gera automaticamente 10 simulações fake, salva todas no banco e retorna o lote em JSON.

GET /simulador/gerar_lote/


Exemplo em ambiente local:

http://127.0.0.1:8000/simulador/gerar_lote/

# Gerar lote em formato ARFF

Gera um lote de simulações fake e exporta automaticamente um arquivo .arff, pronto para uso em ferramentas de machine learning (ex: WEKA).

O arquivo é baixado diretamente pelo navegador.

GET /simulador/lote_arff/


Exemplo em ambiente local:s

http://127.0.0.1:8000/simulador/lote_arff/

## ⚠️Observações importantes

As rotas documentadas no formato GET /rota/ representam a especificação da API, e não devem ser usadas diretamente no navegador.

Para testar localmente, utilize sempre a URL completa, como http://127.0.0.1:8000/....

As mudanças realizadas não alteram a estrutura dos dados, apenas o conteúdo gerado (ex: sintomas mais coerentes), garantindo compatibilidade com outros módulos que consomem a API.