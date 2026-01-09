## Módulo Núcleo – Aluno 5

Cadastro de Pacientes Reais + Upload de Imagens Reais

Este módulo é responsável pela parte real do sistema clínico: cadastro de pacientes verdadeiros, registro de sintomas, possível diagnóstico e upload de imagens reais de exames.

Ele é totalmente separado do módulo do Aluno 6 (Simulador), porque aqui tratamos de dados sensíveis e reais.

A seguir, tudo será explicado da forma mais clara possível. :)

## Como rodar o projeto :

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


##  Diferença de escopo entre o Aluno 5 e o Aluno 6. Por que é importante pontuar ?

# Aluno 5 – Dados Reais (este módulo)

Cadastra pacientes reais.

Registra sintomas e possível diagnóstico.

Faz upload de imagens reais.

As imagens vão para:

/media/imagens_reais/


# Aluno 6 – Dados Simulados

Trabalha com pacientes simulados, criados pelo sistema.

Usa imagens de termografia de teste, não reais.

As imagens ficam em:

/media/termografias/
 /media/simulador_imagens/

# Por que essa separação existe?

Porque softwares clínicos de verdade nunca misturam dados reais com dados simulados.
Isso evita risco de confusão, garante segurança, e mantém o sistema organizado. Além de proteger
a privacidade do paciente.


## Acesso ao Django Admin

O Admin é a parte interna do sistema, usada pela clínica.

>> Como acessar:

>>Rodar o servidor:

python manage.py runserver


Abrir:

http://127.0.0.1:8000/admin/


Entrar com o usuário fornecido pelo grupo (ex.: admsad) e pronto :)

## Cadastro de Pacientes no Admin

No menu >> Pacientes, é possível:

adicionar pacientes

editar pacientes

visualizar exames ligados

verificar sintomas e diagnóstico

>> Campos do Paciente:

Nome completo

CPF

Data de nascimento

Sintomas

Possível diagnóstico

UUID automático (usado pela API)

## Upload de Imagens Reais de Exame

O upload de imagens funciona normalmente pelo Admin, que é inclusive o método mais recomendado.

>> Caminho:

Imagem exames >> Adicionar

Campos disponíveis:

Paciente

Usuário que está enviando

Instituição

Imagem real (arquivo)

Descrição opcional

Tipo de exame (default: Exame Real)

Ao salvar, o arquivo é enviado para:

/media/imagens_reais/


E fica automaticamente vinculado ao paciente.

## API – Endpoints do Paciente

Base URL:

http://127.0.0.1:8000/api/

## Listar ou Criar Pacientes
GET  /api/pacientes/
POST /api/pacientes/


Ecemplo de orpo para criar (POST):

{
  "nome_completo": "Maria da Silva",
  "cpf": "123.456.789-00",
  "data_nascimento": "1980-05-15",
  "sintomas": "Dores de cabeça",
  "possivel_diagnostico": "Indefinido"
}

## Detalhar / Editar / Deletar Paciente
GET    /api/pacientes/<uuid>/
PUT    /api/pacientes/<uuid>/
DELETE /api/pacientes/<uuid>/

## API – Upload de Imagem Real

Este é o endpoint para upload via API:

POST /api/pacientes/<uuid_paciente>/upload-imagem/

⚠️ Sobre o envio de arquivos

O corpo precisa ser multipart/form-data.
Isso significa: a tela padrão do Django REST Framework NÃO aceita esse tipo de envio.

Ou seja:

>> Não funciona pela interface web do DRF (página branca).
>> Funciona pelo Admin.
>> Funciona por clientes HTTP como:

Postman

Thunder Client (VSCode)

Insomnia

# Esse comportamento é normal em APIs reais que trabalham com arquivos.
A interface do DRF foi feita para testar JSON, não para fazer upload.

Exemplo dos campos:

usuario_upload (ID)

instituicao (ID)

descricao_opcional

tipo_imagem

caminho_arquivo (arquivo real)

O UUID do paciente vem da URL.

## Estrutura das Pastas de Mídia

Para evitar misturar imagens reais e simuladas:

/media/imagens_reais/              # Aluno 5 – dados reais
/media/termografias/               # Aluno 6 – imagens base do simulador
/media/simulador_imagens/          # Aluno 6 – imagens processadas

## O que este módulo entrega

Este módulo do Aluno 5 entrega:

CRUD completo de pacientes (Admin + API)

Campos clínicos (sintomas e possível diagnóstico)

Upload de imagens reais funcionando

Separação completa de dados reais x simulados

Endpoints organizados e documentados

Modelos limpos e alinhados ao padrão da área clínica

Padrão profissional igual aos sistemas reais de saúde

## Observação importante

O upload pela API funciona perfeitamente, só não é possível testar pela tela web do DRF.

Isso é normal.
Cerca de 90% das APIs com upload exigem Postman, Thunder ou equivalente.