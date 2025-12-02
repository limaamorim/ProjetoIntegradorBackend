# Sistema de Diagnóstico Termográfico -- Projeto Integrador

Este repositório contém o **projeto integrador completo**, desenvolvido
com foco em diagnóstico termográfico, auditoria, conformidade ANVISA
(RDC 330/2019), integração com **WEKA via CSI**, segurança, logs
estruturados e emissão de laudos.

------------------------------------------------------------------------

# 📌 Objetivo Geral do Sistema

Criar um **sistema completo de apoio ao diagnóstico** composto por:

-   Cadastro e gerenciamento de pacientes\
-   Simulação e processamento de imagens termográficas\
-   Comunicação real ou simulada com o **WEKA**\
-   Registro e auditoria completa das operações\
-   Geração de diagnósticos e laudos\
-   Conformidade com requisitos da **ANVISA -- RDC 330/2019**\
-   Segurança, criptografia, rastreabilidade e controle de acesso

------------------------------------------------------------------------

# 🛡 Requisitos Gerais do Projeto

-   [ ] Conformidade ANVISA: Software regulamentado para saúde\
-   [ ] Auditabilidade total: logs rastreáveis para todas as ações\
-   [ ] Tela de login obrigatória\
-   [ ] Comunicação com **WEKA via CSI (Command Script Interface)**\
-   [ ] Simulação inicial com dados fictícios\
-   [ ] Registro de diagnósticos no banco de dados\
-   [ ] Relatórios por paciente e por período

------------------------------------------------------------------------

# 👥 Distribuição das Atividades por Aluno

## **Aluno 1 -- Especialista ANVISA**

-   Estudo da regulamentação **RDC 330/2019**
-   Definição de requisitos mínimos de segurança e auditoria
-   Criação do checklist de conformidade
-   Avaliação de rastreabilidade, integridade, versionamento e IPs

------------------------------------------------------------------------

## **Aluno 2 -- Sistema de Auditoria**

-   Implementação de logs estruturados (ex.: structlog)
-   Criação da tabela de auditoria no BD
-   Registro obrigatório para:
    -   Login / logout\
    -   Operações críticas\
    -   Acesso a dados sensíveis\
    -   Geração e impressão de laudos\
    -   Erros do sistema

------------------------------------------------------------------------

## **Aluno 3 -- Segurança e Criptografia**

-   Criptografia AES para dados sensíveis\
-   Implementação de RBAC (admin, médico, auditor)\
-   Validações contra SQL Injection e entradas malformadas

------------------------------------------------------------------------

## **Aluno 4 -- Modelo de Dados**

-   Criação das tabelas regulatórias:
    -   **Paciente**\
    -   **Diagnóstico**\
    -   **Laudo**\
    -   **Histórico e auditoria**

------------------------------------------------------------------------

## **Aluno 5 -- CRUD de Pacientes**

-   Endpoints para cadastro, edição e consulta\
-   Validação ANVISA de campos obrigatórios\
-   Geração automática de **UUID** do paciente\
-   Registro de data/hora do diagnóstico

------------------------------------------------------------------------

## **Aluno 6 -- Simulador de Dados**

-   Geração de pacientes fictícios (**Faker**)\
-   Criação de imagens de termografia simuladas\
-   Gerador de resultados aleatórios (modo simulado)

------------------------------------------------------------------------

## **Aluno 7 -- Especialista WEKA**

-   Estudo da documentação e CSI\
-   Preparação dos scripts de classificação\
-   Testes iniciais via terminal

------------------------------------------------------------------------

## **Aluno 8 -- Adaptador WEKA**

-   Implementação da comunicação via **Command Script Interface**\
-   Encapsulamento das chamadas WEKA\
-   Tratamento de erros e tempos limite

------------------------------------------------------------------------

## **Aluno 9 -- Simulador WEKA**

-   Implementação dos modos:
    -   **Real** (via WEKA CSI)\
    -   **Simulado** (respostas randômicas)\
-   Fallback automático\
-   Logs integrados para auditoria

------------------------------------------------------------------------

## **Aluno 10 -- Gerador de Laudos**

-   Template PDF conforme requisitos ANVISA\
-   Inclusão de:
    -   Profissional responsável\
    -   IP de emissão\
    -   Código de verificação\
    -   Versão do modelo IA/WEKA

------------------------------------------------------------------------

## **Aluno 11 -- Interface de Diagnóstico**

-   Endpoint para registrar diagnóstico\
-   Associação com paciente, usuário e arquivo de origem\
-   Integração com auditoria

------------------------------------------------------------------------

## **Aluno 12 -- Relatórios e Auditoria**

-   Relatórios por:
    -   Paciente\
    -   Período\
    -   Profissional\
    -   Conformidade ANVISA\
-   Dashboard de auditoria e rastreabilidade

------------------------------------------------------------------------

# 🗂 Estrutura Recomendada do Repositório

    /database
        ├── create_tables.sql
        └── seed_data.sql

    /backend
        ├── src/
        ├── controllers/
        ├── models/
        ├── services/
        ├── weka/
        ├── logs/
        ├── README.md
        └── ...

    /docs
        ├── checklist_anvisa.pdf
        ├── diagramas_der.png
        ├── documentacao_weka.md
        └── ...

    /frontend
        ├── tela_login.html
        ├── dashboard.html
        └── ...

------------------------------------------------------------------------

# 🔒 Conformidade ANVISA -- RDC 330/2019

Este projeto segue os pontos essenciais:

### ✔ Auditoria completa

Todos os acessos são registrados com: - data e hora\
- id do usuário\
- ação realizada\
- recurso acessado\
- IP de origem

### ✔ Rastreabilidade

Logs não são apagáveis (protegidos por política).\
Cada laudo possui código de verificação único.

### ✔ Versionamento

Toda alteração de laudo gera histórico.

### ✔ Segurança

Criptografia AES para dados sensíveis.\
Controle de acesso baseado em papéis (RBAC).

------------------------------------------------------------------------

# 🧪 Simulador + WEKA + CSI

O sistema possui dois modos:

### **Modo Simulado**

-   Dados gerados pelo Faker\
-   Classificação aleatória\
-   Ideal para versão inicial

### **Modo Real**

-   Comunicação via **WEKA CLI / CSI**\
-   Envio da imagem ou vetor de características\
-   Recebimento do diagnóstico\
-   Registro no BD

O módulo WEKA é completamente logado na auditoria.

------------------------------------------------------------------------

# 📥 Execução

1.  Criar o banco de dados:

```{=html}
<!-- -->
```
    mysql < database/create_tables.sql

2.  Carregar dados de teste:

```{=html}
<!-- -->
```
    mysql < database/seed_data.sql

3.  Iniciar o backend:

```{=html}
<!-- -->
```
    npm install
    npm run dev

4.  Iniciar o frontend: Abra o arquivo `index.html`.

------------------------------------------------------------------------

# 📄 Licença

Projeto acadêmico desenvolvido para fins educacionais.

------------------------------------------------------------------------
