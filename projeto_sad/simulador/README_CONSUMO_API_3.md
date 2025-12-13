## Guia para Consumo da API 

# Este guia foi desenvolvido principalmente para os alunos, que segundo as diretrizes do trabalho, serão responsáveis pelo consumo da API caso haja a necessidade. Entretanto pode ser usado para ajudar qualquer usuário do sistema :)

A API do Simulador foi feita para você consumir dados gerados automaticamente.

Você só precisa fazer requisições HTTP simples.
A API já retorna tudo em JSON, sem precisar configurar nada.

## Como consumir esta API (explicação simples, direta e prática)

A API do Simulador foi construída para ser simples de usar, mesmo para quem nunca consumiu uma API antes.
Abaixo está o passo a passo REAL do que fazer.



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


Exemplo em ambiente local:

http://127.0.0.1:8000/simulador/lote_arff/


## 2. Formatado em JSON automaticamente

Não é necessário configurar nada.
A API sempre responde com JSON, assim:

{
  "id": 12,
  "nome": "José Daniel",
  "cpf_fake": "392.444.222-90",
  "idade": 55,
  "sintomas": "Paciente relata dores no peito...",
  "diagnostico_fake": "Cisto",
  "confianca": 0.88,
  "imagem_url": "/media/simulador_imagens/img1.jpeg",
  "modo": "simulado",
  "data_criacao": "2025-11-28T22:17:00Z"
}

## 3. Como consumir a API (exemplos reais)

Existem 3 formas principais ― qualquer uma funciona.

>> A) Consumindo no navegador (método mais simples)

Basta colar a URL na barra do navegador:

http://127.0.0.1:8000/simulador/gerar/


O Django REST Framework automaticamente exibirá o JSON formatado.

>> B) Consumindo via Postman/Insomnia (para testes profissionais)

Abra o Postman

Clique em New Request

Escolha GET

Cole a URL

Clique em SEND

Pronto. O Postman vai mostrar o JSON na tela.

>> C) Consumindo com código (caso o aluno 9 precise OU quem for consumir a API)
Exemplo com Python:
import requests

r = requests.get("http://127.0.0.1:8000/simulador/gerar/")
dados = r.json()
print(dados)

Exemplo com JavaScript:
fetch("http://127.0.0.1:8000/simulador/gerar/")
  .then(resp => resp.json())
  .then(data => console.log(data));


## Esses códigos fazem exatamente a mesma coisa que o navegador:
mandam GET → recebem JSON → usam as informações.

# 4. Observações importantes sobre o Django
>> 1. Formatos de imagem aceitos

Por padrão, o Django aceita bem:

.jpg

.jpeg

.png

Formatos como .webp podem gerar problemas dependendo da instalação do Pillow.

>> 2. Sobre onde as imagens são salvas

A API usa imagens da pasta:

media/simulador_imagens/


E retorna sempre uma URL completa para que o cliente possa exibir a imagem.

>> 3. Particularidade do Django Admin

Para que a ação “Gerar simulação automaticamente” apareça no admin:

é necessário selecionar ao menos 1 simulação na lista

isso é um comportamento nativo do Django (não é erro no código)

>> 5. Em resumo (para quem vai consumir)

Você só precisa chamar a URL.

Use GET.

Receba o JSON.

Use os dados como quiser.

Nada adicional precisa ser configurado.