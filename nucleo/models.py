import uuid
from django.db import models
from django.contrib.auth.models import User
from .seguranca import EncryptedCharField, EncryptedTextField, EncryptedFileField

# ============================================
# ALUNO 1 e 3: INFRAESTRUTURA E INSTITUIÇÃO
# ============================================
class Instituicao(models.Model):
    """
    Representa a entidade clínica conforme RDC 330.
    Garante a vinculação de dados a uma pessoa jurídica responsável.
    """
    nome_instituicao = models.CharField(max_length=150, verbose_name="Nome da Instituição")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name="Logotipo da Clínica")
    # Validação de formato deve ser feita no Serializer/Form
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True)
    endereco_fisico = models.CharField(max_length=200, null=True, blank=True, verbose_name="Endereço Físico")
    endereco_eletronico = models.EmailField(max_length=200, null=True, blank=True, verbose_name="Email Institucional")
    telefone = models.CharField(max_length=20, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Instituições"

    def __str__(self):
      return self.nome_instituicao


# ============================================
# ALUNO 3: SEGURANÇA E RBAC (Role-Based Access Control)
# Atende a exigência: "Configurar RBAC (papéis: admin, médico, auditor)"
# ============================================
class PerfilUsuario(models.Model):
    """
    Extensão do modelo User nativo do Django para implementar RBAC.
    A segurança de senha (hash/salt) é herdada nativamente do Django (PBKDF2/SHA256).
    """
    PERFIS = (
        ('MEDICO', 'Médico'),         # Acesso: Diagnóstico e Pacientes
        ('TECNICO', 'Técnico'),       # Acesso: Upload de Exames
        ('ADMIN', 'Administrador'),   # Acesso: Gestão de Usuários
        ('AUDITOR', 'Auditor'),       # Acesso: Logs e Relatórios (Leitura)
    )
    
    # Proteção contra SQL Injection é garantida pelo ORM do Django aqui
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="Usuário de Sistema")
    
    registro_profissional = models.CharField(max_length=50, null=True, blank=True, verbose_name="Registro Profissional (CRM/COREN)")
    papel = models.CharField(max_length=10, choices=PERFIS, default='MEDICO', db_column='perfil') # Renomeado para 'papel' via db_column para atender solicitação
    ativo = models.BooleanField(default=True)
    
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT, verbose_name="Instituição de Afiliação") 

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.papel})"

# ============================================
# ALUNO 4 e 5: PACIENTES E DADOS SENSÍVEIS
# Atende a exigência: "Dados pessoais dos pacientes e UUID"
# ============================================
class Paciente(models.Model):
    """
    Armazena dados sensíveis (PII). 
    NOTA DE SEGURANÇA: O campo uuid_paciente garante anonimização em exportações.
    """
    # UUID: Identificador único universal para evitar colisão e permitir anonimização (Exigência ANVISA)
    uuid_paciente = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="ID Único do Paciente")
    cpf = EncryptedCharField(max_length=14, unique=True, null=True, blank=True, verbose_name="CPF")
    
    # Em produção, converter para EncryptedCharField (AES-256) via biblioteca django-fernet-fields
    nome_completo = EncryptedCharField(max_length=150, verbose_name="Nome Completo") 
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento", help_text="Formato: dd/mm/aaaa")
    
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    sintomas = EncryptedCharField(null=True, blank=True)
    possivel_diagnostico = EncryptedCharField(null=True, blank=True)
    
    def __str__(self):
      return self.nome_completo



# ============================================
# ALUNO 5: IMAGENS REAIS DE EXAME
# ============================================

class ImagemExame(models.Model):
    # Quando um paciente é deletado, bloqueia deletar imagem (protege)
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.PROTECT,
        verbose_name="Paciente"
    )

    usuario_upload = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuário que fez o upload"
    )

    instituicao = models.ForeignKey(
        Instituicao,
        on_delete=models.PROTECT,
        verbose_name="Instituição"
    )

    # >>>DESTINO DOS ARQUIVOS REAIS
    caminho_arquivo = models.FileField(
        upload_to='imagens_reais/', 
        verbose_name="Arquivo da Imagem Real"
    )
    data_upload = models.DateTimeField(auto_now_add=True)

    descricao_opcional = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    tipo_imagem = models.CharField(
        max_length=50,
        default='Exame Real'
    )

    def __str__(self):
        return f"Imagem de {self.paciente.nome_completo} ({self.tipo_imagem})"


# ============================================
# ALUNO 6 — MÓDULO DE SIMULAÇÃO
# ============================================
"""
Este espaço está propositalmente vazio.

Todo o conteúdo referente ao Aluno 6
(models, serializers, views e rotas)
fica no módulo próprio do simulador,
separado do núcleo, pois utiliza
apenas IMAGENS FICTÍCIAS geradas para testes.

As imagens simuladas são armazenadas em:
    media/simulador_imagens/

IMPORTANTE:
Os modelos deste arquivo (núcleo) são
exclusivamente do Aluno 5 - CRUD, que trabalha
com DADOS REAIS de pacientes e utiliza
a pasta:
    media/imagens_reais/

Não misturar imagens simuladas com imagens reais.
"""


# ============================================
# ALUNO 7, 8 e 9: INTEGRAÇÃO IA/WEKA
# ============================================
class AnaliseImagem(models.Model):
    """
    Armazena o resultado do processamento da IA.
    Contém campos de checksum para garantir que o resultado não foi alterado (Integridade).
    """
    imagem = models.OneToOneField(ImagemExame, on_delete=models.CASCADE, verbose_name="Imagem Analisada")
    usuario_solicitante = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuário Solicitante")
    
    data_hora_solicitacao = models.DateTimeField(auto_now_add=True)
    data_hora_conclusao = models.DateTimeField(null=True, blank=True)
    
    RESULTADOS = (
        ('Maligno', 'Maligno'),
        ('Benigno', 'Benigno'),
        ('Cisto', 'Cisto'),
        ('Saudavel', 'Saudável'),
    )
    resultado_classificacao = models.CharField(max_length=10, choices=RESULTADOS)
    
    score_confianca = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    # Rastreabilidade do modelo usado (Exigência de Auditoria de IA)
    modelo_versao = models.CharField(max_length=50)
    modelo_checksum = models.CharField(max_length=100) # Garante qual versão da IA gerou o laudo
    hash_imagem = models.CharField(max_length=100) # SHA-256 da imagem original

    class Meta:
        verbose_name_plural = "Análises de Imagem"

    def __str__(self):
        try:
            paciente = self.imagem.paciente.nome_completo
        except Exception:
            paciente = "Paciente desconhecido"

        resultado = self.resultado_classificacao or "Sem resultado"

        return f"Análise #{self.id} - {paciente} ({resultado})"


# ============================================
# ALUNO 10: LAUDOS MÉDICOS
# ============================================
class Laudo(models.Model):
    analise = models.OneToOneField(AnaliseImagem, on_delete=models.CASCADE, verbose_name="Análise de Origem")
    # Apenas usuários com perfil 'MEDICO' devem ser associados aqui (Validado na View)
    usuario_responsavel = models.ForeignKey(PerfilUsuario, on_delete=models.SET_NULL, null=True, verbose_name="Profissional Responsável")
    
    data_hora_emissao = models.DateTimeField(auto_now_add=True)
    texto_laudo_completo = models.TextField() 
    caminho_pdf = models.FileField(upload_to='laudos/', null=True, blank=True)
    
    confirmou_concordancia = models.BooleanField(verbose_name="Confirma Concordância com IA") 
    ip_emissao = models.CharField(max_length=45, verbose_name="IP de Emissão")
    
    # Imutabilidade: Após finalizado, não pode ser editado (RDC 330)
    laudo_finalizado = models.BooleanField(default=False, verbose_name="Finalizado/Bloqueado")
    codigo_verificacao = models.CharField(max_length=50, unique=True) 

    def __str__(self):
        # usa código de verificação (se existir) e paciente (se der)
        codigo = getattr(self, "codigo_verificacao", None) or f"ID {self.id}"
        try:
            paciente = self.analise.imagem.paciente.nome_completo
            return f"Laudo {codigo} - {paciente}"
        except Exception:
            return f"Laudo {codigo}"

# ============================================
# ALUNO 12: VERSIONAMENTO DE DOCUMENTOS
# ============================================
class HistoricoLaudo(models.Model):
    """
    Tabela de versionamento para atender requisitos de auditoria.
    Salva o estado anterior do laudo sempre que houver uma retificação.
    """
    laudo = models.ForeignKey(Laudo, on_delete=models.CASCADE)
    usuario_responsavel = models.ForeignKey(PerfilUsuario, on_delete=models.PROTECT, verbose_name="Usuário da Alteração")
    
    data_hora_alteracao = models.DateTimeField(auto_now_add=True)
    texto_anterior = models.TextField()
    ip_alteracao = models.CharField(max_length=45)

    def __str__(self):
        codigo = getattr(self.laudo, "codigo_verificacao", None) or f"id {self.laudo_id}"
        try:
            usuario = (
                self.usuario_responsavel.usuario.get_full_name()
                or self.usuario_responsavel.usuario.username
            )
        except Exception:
            usuario = "Usuário desconhecido"

        data = self.data_hora_alteracao.strftime("%d/%m/%Y %H:%M")

        return f"Histórico do Laudo {codigo} - {usuario} em {data}"
        
class LaudoImpressao(models.Model):
    laudo = models.ForeignKey(Laudo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT) 
    data_hora_impressao = models.DateTimeField(auto_now_add=True)
    ip_origem = models.CharField(max_length=45)
    local_impressao = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        codigo = getattr(self.laudo, "codigo_verificacao", None) or f"id {self.laudo_id}"
        usuario = self.usuario.get_full_name() or self.usuario.username
        data = self.data_hora_impressao.strftime("%d/%m/%Y %H:%M")

        if self.local_impressao:
            return f"Impressão do Laudo {codigo} - {usuario} em {data} ({self.local_impressao})"

        return f"Impressão do Laudo {codigo} - {usuario} em {data}"

# ============================================
# ALUNO 2: LOGS DE AUDITORIA E CONFORMIDADE
# Atende a exigência: "Trilha de auditoria indelével"
# ============================================
class LogAuditoria(models.Model):
    ACOES = (
        ('LOGIN_SUCESSO', 'Login Bem-Sucedido'),
        ('LOGIN_FALHA', 'Tentativa de Login Falha'), # Detecção de Brute-force
        ('LOGOUT', 'Logout'),

        # Paciente
        ('PACIENTE_CRIADO', 'Paciente Criado'),
        ('PACIENTE_ATUALIZADO', 'Paciente Atualizado'),
        ('PACIENTE_EXCLUIDO', 'Paciente Excluído'),

        ('UPLOAD_IMAGEM', 'Upload de Imagem de Exame'),

        ('ANALISE_SOLICITADA', 'Solicitação de Análise IA'),
        ('ANALISE_CONCLUIDA', 'Análise IA Concluída'),

        ('LAUDO_GERADO', 'Geração de Laudo'),
        ('LAUDO_IMPRESSO', 'Laudo Impresso'),
        ('LAUDO_ALTERADO', 'Laudo Alterado'),

        ('ERRO_SISTEMA', 'Erro Crítico do Sistema'),
        ('ACESSO_RELATORIO', 'Acesso a Relatório/Auditoria'),
    )
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuário Responsável")
    data_hora = models.DateTimeField(auto_now_add=True)
    acao = models.CharField(max_length=50, choices=ACOES) 
    recurso = models.CharField(max_length=100, null=True, blank=True, verbose_name="Recurso Acessado")
    detalhe = models.TextField(null=True, blank=True) # Payload da ação
    ip_origem = models.CharField(max_length=45, verbose_name="IP de Origem")
    
    # Garante que este log não deve ser apagado (Retention Policy)
    protegido = models.BooleanField(default=True) 

    class Meta:
        verbose_name_plural = "Logs de Auditoria"

# OBS: Como estamos usando o ORM do Django (Object Relational Mapping), a validação é nativa. O Django converte automaticamente todos os inputs desse models.py 
# em Prepared Statements no banco. É tecnicamente impossível fazer SQL Injection via input de usuário usando essa arquitetura, pois o driver do banco 
# escapa os caracteres perigosos antes de executar a query. 
# Fizemos assim para garantir segurança máxima sem depender de validação manual propensa a falhas.