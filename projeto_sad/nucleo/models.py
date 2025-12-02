import uuid
from django.db import models
from django.contrib.auth.models import User

# Importa os campos criptografados corretamente
from .seguranca import EncryptedCharField, EncryptedTextField, EncryptedFileField



# ============================================
# ALUNO 1 e 3: INFRAESTRUTURA E INSTITUIÇÃO
# ============================================
class Instituicao(models.Model):
    nome_instituicao = models.CharField(max_length=150, verbose_name="Nome da Instituição")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True)
    endereco_fisico = models.CharField(max_length=200, null=True, blank=True)
    endereco_eletronico = models.EmailField(max_length=200, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Instituições"


# ============================================
# ALUNO 3: SEGURANÇA – RBAC
# ============================================
class PerfilUsuario(models.Model):
    PERFIS = (
        ('MEDICO', 'Médico'),
        ('TECNICO', 'Técnico'),
        ('ADMIN', 'Administrador'),
        ('AUDITOR', 'Auditor'),
    )

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    registro_profissional = models.CharField(max_length=50, null=True, blank=True)
    papel = models.CharField(max_length=10, choices=PERFIS, default='MEDICO')
    ativo = models.BooleanField(default=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT)


# ============================================
# ALUNO 4 e 5: PACIENTES
# ============================================
class Paciente(models.Model):
    uuid_paciente = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    cpf = EncryptedCharField(max_length=14, null=True, blank=True, unique=True)
    nome_completo = EncryptedCharField(max_length=150)
    data_nascimento = EncryptedCharField(max_length=20, null=True, blank=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)


# ============================================
# ALUNO 6: IMAGENS MÉDICAS
# ============================================
class ImagemExame(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    usuario_upload = models.ForeignKey(User, on_delete=models.CASCADE)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT)

    caminho_arquivo = EncryptedFileField(upload_to='termografias/')

    data_upload = models.DateTimeField(auto_now_add=True)
    descricao_opcional = models.CharField(max_length=255, null=True, blank=True)
    tipo_imagem = models.CharField(max_length=50, default='Termografia Mamária')


# ============================================
# ALUNO 7, 8 e 9: IA / WEKA
# ============================================
class AnaliseImagem(models.Model):
    imagem = models.OneToOneField(ImagemExame, on_delete=models.CASCADE)
    usuario_solicitante = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

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

    modelo_versao = models.CharField(max_length=50)
    modelo_checksum = models.CharField(max_length=100)
    hash_imagem = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Análises de Imagem"


# ============================================
# ALUNO 10: LAUDO MÉDICO
# ============================================
class Laudo(models.Model):
    analise = models.OneToOneField(AnaliseImagem, on_delete=models.CASCADE)
    usuario_responsavel = models.ForeignKey(PerfilUsuario, on_delete=models.SET_NULL, null=True)

    data_hora_emissao = models.DateTimeField(auto_now_add=True)

    texto_laudo_completo = EncryptedTextField()

    caminho_pdf = models.CharField(max_length=255, null=True, blank=True)
    confirmou_concordancia = models.BooleanField()
    ip_emissao = models.CharField(max_length=45)

    laudo_finalizado = models.BooleanField(default=False)
    codigo_verificacao = models.CharField(max_length=50, unique=True)


# ============================================
# ALUNO 12: VERSIONAMENTO
# ============================================
class HistoricoLaudo(models.Model):
    laudo = models.ForeignKey(Laudo, on_delete=models.CASCADE)
    usuario_responsavel = models.ForeignKey(PerfilUsuario, on_delete=models.PROTECT)

    data_hora_alteracao = models.DateTimeField(auto_now_add=True)

    texto_anterior = EncryptedTextField()

    ip_alteracao = models.CharField(max_length=45)


class LaudoImpressao(models.Model):
    laudo = models.ForeignKey(Laudo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    data_hora_impressao = models.DateTimeField(auto_now_add=True)
    ip_origem = models.CharField(max_length=45)
    local_impressao = models.CharField(max_length=100, null=True, blank=True)


# ============================================
# ALUNO 2: AUDITORIA
# ============================================
class LogAuditoria(models.Model):
    ACOES = (
        ('LOGIN_SUCESSO', 'Login Bem-Sucedido'),
        ('LOGIN_FALHA', 'Tentativa de Login Falha'),
        ('LOGOUT', 'Logout'),
        ('UPLOAD_IMAGEM', 'Upload de Imagem de Exame'),
        ('ANALISE_SOLICITADA', 'Solicitação de Análise IA'),
        ('ANALISE_CONCLUIDA', 'Análise IA Concluída'),
        ('LAUDO_GERADO', 'Geração de Laudo'),
        ('LAUDO_IMPRESSO', 'Laudo Impresso'),
        ('LAUDO_ALTERADO', 'Laudo Alterado'),
        ('ERRO_SISTEMA', 'Erro Crítico do Sistema'),
        ('ACESSO_RELATORIO', 'Acesso a Relatório/Auditoria'),
    )

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    acao = models.CharField(max_length=50, choices=ACOES)
    recurso = models.CharField(max_length=100, null=True, blank=True)

    detalhe = EncryptedTextField(null=True, blank=True)

    ip_origem = models.CharField(max_length=45)
    protegido = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Logs de Auditoria"
        
class Simulacao(models.Model):
    nome = models.CharField(max_length=150)
    cpf_fake = models.CharField(max_length=14)
    idade = models.IntegerField()
    sintomas = models.TextField()
    diagnostico_fake = models.CharField(max_length=50)
    confianca = models.FloatField()
    imagem_escolhida = models.FileField(upload_to='simulador/')
    modo = models.CharField(max_length=20, default='simulado')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Simulação {self.id} - {self.nome}"
 