
## Projeto Integrador — Simulador de Dados (Aluno 6)

Olá :)

Este módulo faz parte do Projeto Integrador, onde cada aluno ficou responsável por um componente da aplicação clínica.
O Aluno 6 é responsável pelo Simulador de Dados: gerar pacientes falsos, associar imagens e disponibilizar tudo por meio de uma API REST.

O objetivo é fornecer aos alunos 7 e 8 dados brutos para que possam ser processados para que o Aluno 9 tenha uma fonte de dados realista, seja no modo simulado (fake) ou real (via WEKA).
No caso desta parte, a API oferece dados simulados que podem servir para aprendizado de máquina ou para serem usados em testes e apresentações evitando usar dados de pacientes reais.

## Funcionalidades Principais

V Geração automática de pacientes fake (dados sintéticos)
V Associação aleatória com imagens armazenadas no projeto
V Registro completo no banco SQLite
V API REST para criação, listagem e detalhamento das simulações
V Página administrativa no Django para controle manual
V Respostas 100% em JSON, prontas para consumo externo

## Objetivo do Aplicativo

O módulo Simulador tem 3 grandes funções:

Gerar simulações automáticas (nome, idade, sintomas, diagnóstico fake, confiança, imagem aleatória)

Salvar tudo no banco de dados SQLite, sem interferir nos dados do CRUD,onde neste exercício acadêmico representam os dados reais dos pacientes 

Fornecer uma API REST limpa e funcional, para consumo dos alunos responsável 

## Como rodar o projeto

# Caso você comece a ver o projeto por aqui,não esqueça de seguir estes passos :)

>> 1. Ative o ambiente virtual
venv\Scripts\activate

>> 2. Instale as dependências

Dentro da pasta onde está o requirements.txt:

pip install -r requirements.txt

>> 3. Rode o servidor
python manage.py runserver

>> 4. Acesse o admin
http://127.0.0.1:8000/admin/

## Estrutura do Projeto

projeto_sad/
    simulador/
        models.py
        admin.py
        views.py
        urls.py
        services.py


É pelo admin que você também pode inserir imagens manualmente em media/simulador_imagens/.
   
## Imagens usadas pelo simulador:

media/
    simulador_imagens/

Essas imagens são escolhidasaleatoriamente para cada fake gerado.
As imagens são populadas no banco de dados manualmente 
As imagens que servem de base para a escolha aleatória são colocadas na pasta termografias/ dentro da pasta simulador_imagens/. >>

media/
    simulador_imagens/
                     termografias/



Entretanto,as imagens geradas pelos facientes fictícios são armazenadas diretamente na pasta simulador_imagens/ >>

media/
    simulador_imagens/


## Como funciona a geração de simulações :

A cada chamada ao endpoint /simulador/gerar/:

Um nome aleatório é criado com Faker

Um CPF falso é gerado

Idade, sintomas e diagnóstico fake são criados

Uma imagem aleatória da pasta media/simulador_imagens/termografias é escolhida

Os dados são salvos no banco

Tudo é retornado em JSON

Exemplo de retorno:

{
  "id": 28,
  "nome": "Dr. João Miguel da Paz",
  "cpf_fake": "209.943.881-50",
  "idade": 45,
  "sintomas": "Paciente relata desconforto...",
  "diagnostico_fake": "Benigno",
  "confianca": 0.87,
  "imagem_url": "http://127.0.0.1:8000/media/simulador_imagens/caso3.jpeg"
}


## RESUMO DE TODAS AS ROTAS DA API DO SIMULADOR (endpoints disponíveis) 

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


Exemplo em ambiente local:

http://127.0.0.1:8000/simulador/lote_arff/



## Django Admin

O Django Admin permite visualizar e gerar simulações manualmente.

O menu aparece como:

Simulador
   • Simulações


Dentro da tela de listagem, existe um botão especial:

Ações:
    Gerar simulação automaticamente


Isso dispara o serviço de geração fake via admin

## Tecnologias utilizadas

Python 3.12

Django 5.2.8

Django REST Framework

Faker

SQLite

Pillow (para imagens)


## Limitações conhecidas

A API não faz validações de dados enviados manualmente (não é necessário para este projeto).

Apenas GET/POST foram implementados conforme exigido.

O sistema usa SQLite por compatibilidade com o projeto base.

A API serve apenas dados simulados; não faz análise real.


## Observações importantes sobre o Django e uso da aplicação

# 1 Por que a opção “Gerar simulação automaticamente” só aparece quando marco um item?

O Django funciona assim em todos os projetos, não é algo específico do nosso código:

O menu de ações do admin só aparece completamente quando pelo menos um item está marcado na lista.

Mesmo que a ação não use o item marcado, o Django exige a seleção apenas para liberar o botão.

Ou seja:

Se nada for marcado, a ação não aparece.
Isso não é bug, é uma regra do Django.

Como usar:

Entre no admin >> Simulações

Marque qualquer simulação na caixinha à esquerda

Abra o menu Ações

Selecione “Gerar simulação automaticamente”

Clique em Ir

A simulação marcada não é alterada.
Ela serve apenas para “habilitar” o menu. É assim mesmo :)

# 2. Por que algumas imagens funcionam e outras não?

O Django aceita vários formatos, mas em testes práticos:

**JPEG / JPG são os formatos mais seguros.**

Formatos como WEBP, apesar de funcionarem em alguns lugares, podem criar comportamento inconsistente dependendo do navegador e do painel do admin.

Por isso, no projeto:

**Use preferencialmente imagens .jpg ou .jpeg na pasta media/simulador_imagens/.**

Assim evita incompatibilidades e mantém tudo funcionando igual para todos do grupo.

# 3. Sobre navegar usando Edge

Durante o desenvolvimento, o Edge apresentou:

comportamento inconsistente no admin,

atraso para carregar botões,

erros falsos por cache do navegador.

Por segurança:

Use **Chrome ou Firefox** para acessar o Admin e os endpoints da API.

Se algo “sumir”, antes de achar que é bug:

troque de navegador;

limpe o cache;

teste novamente.

## Recomendação prática:

Para acessar:

http://127.0.0.1:8000/admin/ (Django Admin)

http://127.0.0.1:8000/simulador/... (endpoints da API)

prefira usar Chrome ou Firefox.

Se alguma coisa parecer “sumir” ou “não aparecer”:

primeiro teste em outro navegador,

depois limpe o cache,

só então cogite a possibilidade de erro no código :)

## Conclusão

O módulo do Aluno 6 está:

V Alinhado ao PDF da professora
V Integrado ao banco
V Oferecendo endpoints REST prontos 
v Entregue com clareza e organização 


