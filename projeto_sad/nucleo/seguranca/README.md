## Segurança no Projeto – Visão Geral

Este repositório implementa um conjunto robusto de mecanismos de segurança para proteger dados clínicos sensíveis, atendendo aos princípios da RDC 330/2019, LGPD, e boas práticas modernas de desenvolvimento seguro.

## Criptografia AES-256 (Dados em Repouso)

Todos os dados sensíveis são criptografados automaticamente antes de serem persistidos no banco — inclusive utilizando AES-256 no modo GCM, que garante:

✔ Confidencialidade
✔ Integridade (autenticação via tag)
✔ Não-repúdio da estrutura do dado

## Campos criptografados

CPF do paciente

Nome completo

Datas de nascimento

Conteúdo completo dos laudos

Texto de histórico de laudo

Detalhes de auditoria

Arquivos de imagem (termo/foto)

PDFs de laudo

## Como funciona

Os arquivos dentro de nucleo/seguranca/ implementam:

crypto_utils.py → Funções encrypt_value() e decrypt_value()

EncryptedCharField / EncryptedTextField → Criptografia automática no banco

EncryptedFileField → Usa EncryptedStorage para criptografar binários

EncryptedStorage → Criptografa arquivos (AES-256-GCM) antes de salvar em disco

## Chave de Criptografia

A chave AES deve estar definida em:
.env
AES_KEY=chave_base64_ou_hex_32_bytes

## RBAC – Controle de Acesso Baseado em Papéis

O sistema implementa autenticação e autorização com papéis:

ADMIN

MÉDICO

TÉCNICO

AUDITOR

O modelo PerfilUsuario complementa o User nativo e garante:

✔ Permissões por perfil
✔ Acesso restrito a dados clínicos
✔ Auditoria das ações críticas

Cada ação relevante feita por um usuário é registrada automaticamente.

## Auditoria Imutável

A aplicação segue o princípio de auditoria inviolável, incluindo:

Logs de login/logout

Uploads de imagens

Geração e alteração de laudos

Acesso a relatórios

Erros críticos

O modelo LogAuditoria:

✔ impede edição
✔ impede exclusão
✔ criptografa detalhes sensíveis
✔ registra IP, usuário e timestamp

O painel Admin exibe logs apenas em modo leitura, protegendo a integridade do histórico.

## Armazenamento Seguro de Arquivos

Imagens médicas e PDFs são tratados como dados sensíveis.

## Mecanismos usados

✔ EncryptedStorage → criptografa o arquivo antes de salvar
✔ EncryptedFileField → substitui FileField nos modelos
✔ AES-256-GCM aplicado a qualquer binário

Mesmo que alguém copie manualmente os arquivos do media/, eles estarão ilegíveis.

## Hash e Verificação

Alguns módulos incluem:

Hash de imagens para rastreabilidade

Códigos de verificação para laudos

Metadados versionados no histórico

## Boas Práticas Adotadas

Nenhum dado sensível é armazenado em texto puro

Todas as operações críticas geram log

Acesso controlado por RBAC

Variáveis sensíveis ficam fora do código (via .env)

Arquivos de mídia nunca ficam expostos sem criptografia

Auditoria não pode ser modificada nem excluída

## Requisitos para o Sistema Operar com Segurança

Certifique-se de configurar:

DEBUG=False
ALLOWED_HOSTS=[...]
AES_KEY=chave_32_bytes
SECRET_KEY=<segredo_do_django>
SECURE_SSL_REDIRECT=True


E utilizar HTTPS em produção.