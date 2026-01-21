import uuid
import hashlib
import re  # Importação para sanitizar o CPF
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .seguranca import EncryptedCharField, EncryptedTextField, EncryptedFileField

# ============================================
# ALUNO 1 e 3: INFRAESTRUTURA E INSTITUIÇÃO
# ============================================
class Instituicao(models.Model):
    nome_instituicao = models.CharField(max_length=150, verbose_name="Nome da Instituição")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name="Logotipo da Clínica")
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True)
    endereco_fisico = models.CharField(max_length=200, null=True, blank=True, verbose_name="Endereço Físico")
    endereco_eletronico = models.EmailField(max_length=200, null=True, blank=True, verbose_name="Email Institucional")
    telefone = models.CharField(max_length=20, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Instituições"

    def __str__(self):
      return self.nome_instituicao


# ============================================
# ALUNO 3: SEGURANÇA E RBAC
# ============================================
class PerfilUsuario(models.Model):
    PERFIS = (
        ('MEDICO', 'Médico'),
        ('TECNICO', 'Técnico'),
        ('ADMIN', 'Administrador'),
        ('AUDITOR', 'Auditor'),
    )
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="Usuário de Sistema")
    registro_profissional = models.CharField(max_length=50, null=True, blank=True, verbose_name="Registro Profissional (CRM/COREN)")
    papel = models.CharField(max_length=10, choices=PERFIS, default='MEDICO', db_column='perfil')
    ativo = models.BooleanField(default=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT, verbose_name="Instituição de Afiliação") 

    def __str__(self):
        return f"{self.usuario.username} ({self.get_papel_display()})"


# ============================================
# ALUNO 4 e 5: PACIENTES E DADOS SENSÍVEIS
# ============================================
class Paciente(models.Model):
    uuid_paciente = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="ID Único do Paciente")
    cpf = EncryptedCharField(max_length=14, unique=True, null=True, blank=True, verbose_name="CPF")
    nome_completo = EncryptedCharField(max_length=150, verbose_name="Nome Completo") 
    data_nascimento = EncryptedCharField(null=True, blank=True, verbose_name="Data de Nascimento")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    sintomas = EncryptedCharField(null=True, blank=True)
    possivel_diagnostico = EncryptedCharField(null=True, blank=True)
    
    # --- [MANTIDO] Lógica de Sanitização de CPF ---
    def save(self, *args, **kwargs):
        """
        Formata CPF para 000.000.000-00 automaticamente.
        """
        if self.cpf:
            # 1. Remove tudo que NÃO for número
            apenas_numeros = re.sub(r'\D', '', str(self.cpf))
            
            # 2. Se tiver 11 dígitos, aplica a máscara padrão
            if len(apenas_numeros) == 11:
                self.cpf = f"{apenas_numeros[:3]}.{apenas_numeros[3:6]}.{apenas_numeros[6:9]}-{apenas_numeros[9:]}"
        
        super().save(*args, **kwargs)
    # -------------------------------------------
    
    def __str__(self):
      return self.nome_completo


# ============================================
# ALUNO 5: IMAGENS REAIS DE EXAME
# ============================================
class ImagemExame(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, verbose_name="Paciente")
    usuario_upload = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário que fez o upload")
    instituicao = models.ForeignKey(Instituicao, on_delete=models.PROTECT, verbose_name="Instituição")
    caminho_arquivo = models.FileField(upload_to='imagens_reais/', verbose_name="Arquivo da Imagem Real")
    data_upload = models.DateTimeField(auto_now_add=True)
    descricao_opcional = models.CharField(max_length=255, null=True, blank=True)
    tipo_imagem = models.CharField(max_length=50, default='Exame Real')

    def __str__(self):
        return f"Imagem de {self.paciente.nome_completo} ({self.tipo_imagem})"


# ============================================
# ALUNO 7, 8 e 9: INTEGRAÇÃO IA/WEKA (RESTAURADO!)
# ============================================
class AnaliseImagem(models.Model):
    imagem = models.OneToOneField(ImagemExame, on_delete=models.CASCADE, verbose_name="Imagem Analisada")
    usuario_solicitante = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuário Solicitante")
    data_hora_solicitacao = models.DateTimeField(auto_now_add=True)
    data_hora_conclusao = models.DateTimeField(null=True, blank=True)
    
    RESULTADOS = (
        ('AGUARDANDO', 'Aguardando Processamento (IA)'),
        ('Maligno', 'Maligno'),
        ('Benigno', 'Benigno'),
        ('Cisto', 'Cisto'),
        ('Saudavel', 'Saudável'),
        ('ERRO', 'Erro no Processamento'),
    )
    
    resultado_classificacao = models.CharField(max_length=25, choices=RESULTADOS, default='AGUARDANDO', verbose_name="Resultado da Classificação")
    score_confianca = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    modelo_versao = models.CharField(max_length=50, default="Simulador-Weka-J48-v3.5", verbose_name="Versão do Modelo IA")
    modelo_checksum = models.CharField(max_length=100, default="chk_sim_auto_x98y76", verbose_name="Checksum do Modelo")
    hash_imagem = models.CharField(max_length=100, default="Aguardando processamento...", verbose_name="Hash SHA-256 (Integridade)")

    class Meta:
        verbose_name_plural = "Análises de Imagem"

    def __str__(self):
        try:
            nome_paciente = self.imagem.paciente.nome_completo
            data = self.data_hora_solicitacao.strftime('%d/%m/%Y')
            return f"Análise de {nome_paciente} ({data})"
        except:
            return f"Análise {self.id}"

    def save(self, *args, **kwargs):
        """
        MÁGICA DA AUTOMAÇÃO (INTEGRAÇÃO RESTAURADA)
        """
        # 1. Calcular Hash SHA-256
        if (not self.hash_imagem or self.hash_imagem == "Aguardando processamento...") and self.imagem:
            try:
                sha256_hash = hashlib.sha256()
                if hasattr(self.imagem.caminho_arquivo, 'open'): self.imagem.caminho_arquivo.open('rb')
                for chunk in self.imagem.caminho_arquivo.chunks(): sha256_hash.update(chunk)
                self.hash_imagem = sha256_hash.hexdigest()
            except Exception:
                self.hash_imagem = "ERRO_LEITURA_ARQUIVO"

        # 2. SIMULADOR DE INTEGRAÇÃO
        if self.resultado_classificacao == 'AGUARDANDO':
            if self.hash_imagem and "ERRO" not in self.hash_imagem and "Aguardando" not in self.hash_imagem:
                self.resultado_classificacao = 'Benigno'
                self.score_confianca = 0.985
                self.data_hora_conclusao = timezone.now()
        super(AnaliseImagem, self).save(*args, **kwargs)


# ============================================
# ALUNO 10: LAUDOS MÉDICOS (RESTAURADO!)
# ============================================
class Laudo(models.Model):
    analise = models.OneToOneField(AnaliseImagem, on_delete=models.CASCADE, verbose_name="Análise de Origem")
    usuario_responsavel = models.ForeignKey(PerfilUsuario, on_delete=models.SET_NULL, null=True, verbose_name="Profissional Responsável")
    
    data_hora_emissao = models.DateTimeField(auto_now_add=True)
    texto_laudo_completo = models.TextField() 
    caminho_pdf = models.FileField(upload_to='laudos/', null=True, blank=True)
    
    confirmou_concordancia = models.BooleanField(default=True, verbose_name="Confirma Concordância com IA") 
    
    ip_emissao = models.CharField(max_length=45, default="127.0.0.1 (Registro Interno)", verbose_name="IP de Emissão")
    laudo_finalizado = models.BooleanField(default=False, verbose_name="Finalizado/Bloqueado")
    codigo_verificacao = models.CharField(max_length=50, unique=True, default="Será gerado ao Salvar", verbose_name="Código de Verificação") 

    def __str__(self):
        try:
            nome = self.analise.imagem.paciente.nome_completo
            return f"Laudo: {nome} (Emitido em {self.data_hora_emissao.strftime('%d/%m/%Y')})"
        except:
            return f"Laudo {self.id}"

    def save(self, *args, **kwargs):
        if not self.codigo_verificacao or self.codigo_verificacao == "Será gerado ao Salvar":
            self.codigo_verificacao = str(uuid.uuid4())[:8].upper()

        if not self.ip_emissao:
            self.ip_emissao = "127.0.0.1 (Registro Interno)"
        
        if not self.laudo_finalizado:
            self.laudo_finalizado = True 

        super(Laudo, self).save(*args, **kwargs)


# ============================================
# ALUNO 12: VERSIONAMENTO DE DOCUMENTOS
# ============================================
class HistoricoLaudo(models.Model):
    laudo = models.ForeignKey(Laudo, on_delete=models.CASCADE)
    usuario_responsavel = models.ForeignKey(PerfilUsuario, on_delete=models.PROTECT, verbose_name="Usuário da Alteração")
    data_hora_alteracao = models.DateTimeField(auto_now_add=True)
    texto_anterior = models.TextField()
    ip_alteracao = models.CharField(max_length=45)
    
    def __str__(self):
        return f"Histórico Laudo {self.laudo.id} - {self.data_hora_alteracao}"
        
class LaudoImpressao(models.Model):
    laudo = models.ForeignKey(Laudo, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT) 
    data_hora_impressao = models.DateTimeField(auto_now_add=True)
    ip_origem = models.CharField(max_length=45)
    local_impressao = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Impressão Laudo {self.laudo.id} por {self.usuario}"

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
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuário Responsável")
    data_hora = models.DateTimeField(auto_now_add=True)
    acao = models.CharField(max_length=50, choices=ACOES) 
    recurso = models.CharField(max_length=100, null=True, blank=True, verbose_name="Recurso Acessado")
    detalhe = models.TextField(null=True, blank=True) 
    ip_origem = models.CharField(max_length=45, verbose_name="IP de Origem")
    protegido = models.BooleanField(default=True) 

    class Meta:
        verbose_name_plural = "Logs de Auditoria"