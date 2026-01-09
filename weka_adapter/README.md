Projeto Integrador — Serviço de Laudos e Segurança (Alunos 9 e 10)

Este módulo é o componente final do fluxo clínico do Projeto Integrador. Ele é responsável por transformar os dados processados em documentos oficiais, garantindo a integridade, a segurança e a validade jurídica das informações.

O trabalho é uma colaboração técnica onde o Aluno 9 gerencia o fluxo de adaptação de dados (Weka Adapter) e o Aluno 10 garante a camada de segurança de elite (Criptografia e Auditoria).

Funcionalidades Principais

Criptografia AES-256 GCM: Proteção de dados sensíveis e arquivos binários em repouso.



Geração Dinâmica de PDF: Criação de laudos médicos profissionais com ReportLab e Pillow.



Descriptografia Just-in-Time: Processamento de imagens institucionais em memória para o PDF.


Assinatura Digital via QR Code: Validação de autenticidade externa integrada ao documento.

Trilha de Auditoria (RDC 330): Registro automático de cada emissão e impressão de laudo.

Objetivo do Aplicativo
O módulo tem 3 grandes funções:


Segurança de Dados: Criptografar automaticamente campos de texto e arquivos antes de serem salvos no banco de dados.



Geração de Documentos: Produzir laudos médicos com layout oficial, marcas d'água e logomarcas institucionais.

Garantia de Autenticidade: Disponibilizar um mecanismo de conferência via QR Code para validar o documento em portais externos.

Como rodar o projeto
Ative o ambiente virtual venv\Scripts\activate

Instale as dependências pip install -r requirements.txt

Configure a Segurança Certifique-se de que a AES_KEY está configurada no seu arquivo .env para que a descriptografia funcione.

Rode o servidor python manage.py runserver 8001

Estrutura do Projeto
Plaintext

projeto_sad/
    weka_adapter/
        services/
            report_generator.py  # Motor de geração de PDFs
        utils/
            pdf_base.py          # Estilos e marcas d'água
    seguranca/
        crypto_utils.py          # Lógica AES-GCM
        encrypted_storage.py     # Criptografia de arquivos em disco
        encrypted_fields.py      # Campos de banco criptografados
Tratamento de Imagens e Logos
As imagens institucionais são tratadas com rigor técnico para evitar exposição:


Armazenamento: São salvas criptografadas na pasta media/logos/.


Processamento: O leitor de imagens descriptografa o arquivo em memória.


Renderização: A imagem é convertida para RGB via Pillow e inserida no PDF na coordenada otimizada (Y=22.5cm) para garantir visibilidade total.

Tecnologia de Segurança (AES-256 GCM)
A cada salvamento de dado:

Um Nonce (número único) de 12 bytes é gerado.


O dado é criptografado e gera uma Tag de integridade.


O pacote final é armazenado em Base64 no banco de dados.

Na leitura, o sistema verifica a autenticidade antes de exibir o dado.

Tecnologias Utilizadas
Python 3.12

Django 5.2.8

PyCryptodome (Criptografia AES-GCM)

ReportLab (Geração de PDF)

Pillow (Processamento de Imagens)

QRCode (Assinatura Digital)

Observações Técnicas Importantes
Coordenadas de Layout: O sistema utiliza o sistema de coordenadas do ReportLab (de baixo para cima). O logotipo institucional está fixado em Y=22.5cm e X=15.0cm para alinhamento profissional à direita.


Segurança de Arquivos: O EncryptedStorage sobrescreve os métodos padrão do Django para garantir que nenhum arquivo "aberto" toque o disco do servidor.

Navegador Recomendado: Utilize Chrome ou Firefox. O cache de PDFs de alguns navegadores pode mostrar versões antigas de laudos durante o desenvolvimento.

Conclusão
O módulo dos Alunos 9 e 10 está:

Alinhado aos requisitos de proteção de dados (LGPD).

Integrado ao fluxo de análise do Weka.

Oferecendo documentos profissionais, seguros e validados.