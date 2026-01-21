# Sistema de Diagnóstico Termográfico — Projeto Integrador

Este repositório contém o **projeto integrador completo**, desenvolvido em **Python/Django**, 
com foco em diagnóstico termográfico, segurança, auditoria e integração de Inteligência Artificial.
O sistema opera sob uma arquitetura **Monolítica Modular**, garantindo a comunicação fluida entre o Núcleo
(Backend), o Simulador de Exames e o Motor de IA (Weka), utilizando padrões de projeto avançados como o **Adapter**.

---

## 📌 Objetivo Geral do Sistema

Criar um **sistema completo de apoio ao diagnóstico** composto por:
* ✅ **Cadastro e gerenciamento seguro** de pacientes (Base Sólida).
* ✅ **Simulação Avançada:** Geração de dados clínicos e vínculo com imagens termográficas reais.
* ✅ **Integração IA:** Comunicação estruturada com módulo WEKA via **Padrão Adapter**.
* ✅ **Padronização:** Formatação automática de dados sensíveis (CPF) e conformidade com requisitos da ANVISA.
* ✅ **Automação:** Ferramentas para geração de lotes de exames para testes de carga.
* ✅ **Laudos Automatizados:** Emissão de documentos PDF auditáveis com validação via QR Code.
* ✅ **Auditoria Total:** Rastreabilidade completa de ações de usuários e versionamento de documentos médicos.

---

## 🛡 Tecnologias e Arquitetura

* **Linguagem:** Python 3.x
* **Framework:** Django & Django REST Framework
* **Banco de Dados:** SQLite (Desenvolvimento)
* **Design Pattern:** Adapter Pattern (Para desacoplamento do módulo de IA)
* **Segurança:** Criptografia AES-256 GCM, Sanitização de dados, Hash de senhas e proteção contra CSRF.
* **Documentação:** ReportLab e Pillow (Processamento de imagem e PDF em memória).
* **Arquitetura:** Monolítica Modular com Design Pattern Adapter.

---

## 👥 Status das Entregas 

### 🔹 Aluno 1 — ANVISA & Compliance
* **Regulamentação:** Estudo aprofundado e mapeamento da norma **RDC 330/2019**.
* **Requisitos:** Definição dos requisitos mínimos de segurança, auditoria e criação do checklist de conformidade.
* **Avaliação:** Análise de critérios para rastreabilidade, integridade, versionamento e registro de IPs.

### 🔹 Aluno 2 — Planejamento de Auditoria
* **Logs Estruturados:** Definição teórica dos registros de auditoria detalhados.
* **Rastreabilidade:** Especificação dos campos obrigatórios no Banco de Dados para eventos de: Login/Logout, operações de escrita/leitura e acesso a dados sensíveis.
* **Laudos:** Definição dos parâmetros para geração e impressão de laudos auditáveis.

### 🔹 Aluno 3 — Segurança e Criptografia (RBAC)
* **Proteção de Dados:** Implementação de Criptografia AES para campos sensíveis.
* **Controle de Acesso (RBAC):** Definição de papéis e permissões (Administrador, Médico, Auditor).
* **Blindagem:** Implementação de validações de segurança contra SQL Injection e tratamento de entradas malformadas.

### 🔹 Aluno 4 — Arquitetura Base & Integração (Tech Lead)
* **Definição da Arquitetura:** Estruturação inicial do projeto Django, configurações de segurança (`settings.py`) e rotas principais (`urls.py`).
* **Modelagem de Dados:** Criação da estrutura do Paciente (Núcleo) e regras de negócio.
* **Sanitização:** Implementação da formatação automática de CPF (`000.000.000-00`) em todo o sistema.
* **Integração Final:** Conexão dos módulos do Aluno 6 (Simulador) e Aluno 7/8 (IA) ao sistema central.

### 🔹 Aluno 5 — CRUD & Interface
* Endpoints para cadastro, edição e consulta de pacientes.
* Validação de campos obrigatórios conforme regras de negócio da base criada pelo Aluno 4.

### 🔹 Aluno 6 — Simulador de Dados
* Geração de dados demográficos e clínicos fictícios (biblioteca `Faker`).
* **Vínculo com Imagens Reais:** O simulador seleciona termografias reais de um repositório controlado (`media/`) para garantir fidelidade visual.
* API interna para fornecimento de dados de teste.

### 🔹 Aluno 7 — WEKA (Módulo IA)
* Estruturação do módulo de Inteligência Artificial.
* Definição das regras de classificação e endpoints de monitoramento de status do motor.

### 🔹 Aluno 8 — Adaptador WEKA (Integração)
* **Implementação do Adapter Pattern:** Criação de uma camada de tradução que isola o Django da complexidade do motor Weka (Java).
* **Simulação de Diagnóstico:** O adaptador recebe os dados do simulador e retorna classificações (Benigno/Maligno/Cisto) via JSON, permitindo testes de front-end rápidos e desacoplados.

### 🔹 Aluno 9 — Adaptação de Dados e Fluxo IA
* **Refinamento do Adapter:** Otimização da camada de tradução para integração direta com o fluxo de laudos.
* **Consumo de Diagnósticos:** Lógica para transformar os resultados do motor de IA em dados estruturados para o prontuário.

### 🔹 Aluno 10 — Segurança Avançada e Laudos Digitais
* **Proteção AES-256 GCM:** Implementação de EncryptedStorage e campos criptografados para blindagem de dados e imagens.
* **Serviço de Laudos (ReportService):** Geração de PDFs com renderização de logos criptografadas.
* **Conformidade RDC 330:** Rastreabilidade de acessos, registro de IPs e validação de autenticidade via QR Code.

### 🔹 Aluno 11 — Implementação de Logs de Auditoria
* **Motor de Auditoria:** Desenvolvimento do modelo `LogAuditoria` para persistência de eventos críticos.
* **Rastreamento de Eventos:** Implementação da captura automática de Login, Logout, Upload de Imagens, Geração de Laudos e Erros de Sistema.
* **Segurança do Log:** Registro imutável de IP de Origem, Usuário Responsável e Data/Hora exata da ação.

### 🔹 Aluno 12 — Versionamento e Controle de Impressão
* **Histórico de Laudos:** Implementação do modelo `HistoricoLaudo` que salva versões anteriores do documento sempre que há uma retificação, garantindo a integridade do prontuário.
* **Rastreabilidade de Impressão:** Desenvolvimento do módulo `LaudoImpressao`, que registra quem imprimiu o documento, quando e a partir de qual estação de trabalho (IP), atendendo aos requisitos de controle de cópias físicas.

---

## 🗂 Estrutura do Projeto 

```text
projeto_sad/
│
├── manage.py             # Gerenciador do Django
├── .env                  # Chaves de segurança (AES_KEY)
│
├── projeto_sad/          # Configurações Globais (Settings e URLs)
│
├── nucleo/               # Core do Sistema (Models, Views, Admin)
│   ├── models.py         # Classes Principais (Paciente, Laudo, Logs)
│   ├── seguranca/        # Módulo de Proteção (Aluno 10)
│   │   ├── crypto_utils.py       # Lógica AES-GCM
│   │   └── encrypted_storage.py  # Storage de arquivos criptografados
│
├── simulador/            # App Gerador de Exames (Aluno 6)
│
├── weka_adapter/         # App Adaptador e Laudos (Alunos 8 e 9)
│   ├── services/
│   │   └── report_generator.py # Motor de PDF e Imagem
│   └── adapters.py       # Padrão Adapter (Tradução IA)
│
└── media/                # Repositório de Arquivos (Protegido)
    ├── logos/            # Logos institucionais criptografados
    └── laudos/           # Saída de laudos auditáveis

```
## 📥 Como Rodar o Projeto

Este projeto já inclui o banco de dados pré-populado e as dependências configuradas para facilitar a apresentação.

### 1. Pré-requisitos
* Python 3.8 ou superior instalado.

### 2. Instalação
Clone o repositório e entre na pasta:
```bash
git clone <https://github.com/limaamorim/ProjetoIntegradorBackend.git>
cd projeto_sad
```
Crie e ative um ambiente virtual (Recomendado):
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```
Instale as dependências:
```bash
pip install -r requirements.txt
```
### 3. Execução
Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```
### 4. Testando a Integração
* **Acesso ao Painel Admin:** Abra http://127.0.0.1:8000/admin/
    * **Usuário:** `Admsad`
    * **Senha:** `Admsad123`
* **API Simulador:** http://127.0.0.1:8000/simulador/gerar/
* **API Adaptador IA:** http://127.0.0.1:8000/weka-adapter/classificar/

## 🧪 Funcionalidade de Automação (Destaque)

Para facilitar a auditoria e os testes de carga, foi implementada uma **Action no Django Admin**:

1.  Acesse a aba **Simulações** no Admin.
2.  Selecione a ação **"Gerar lote (10 simulações)"** no menu superior.
3.  Clique em **Go (Ir)**.

**O sistema irá automaticamente:**
* Gerar 10 pacientes via módulo do Aluno 6.
* Buscar imagens reais na pasta local.
* Classificar cada caso via Adaptador do Aluno 8.
* Salvar tudo no banco de dados com formatação correta.
* Criptografar os dados sensíveis e o diagnóstico utilizando o padrão AES-256 GCM .
* Gerar e salvar o Laudo em PDF com logomarca institucional descriptografada em tempo real.
* Registrar a trilha de auditoria de IP e emissão no banco de dados

------------------------------------------------------------------------

# 📄 Licença

Projeto acadêmico desenvolvido para fins educacionais.

------------------------------------------------------------------------
