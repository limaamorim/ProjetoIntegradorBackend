from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect

# [ALUNO 10] Importação do serviço de geração de relatórios
from weka_adapter.services.report_generator import ReportService

# Importação centralizada dos modelos do projeto
from .models import (
    Instituicao, PerfilUsuario, Paciente, ImagemExame, 
    AnaliseImagem, Laudo, HistoricoLaudo, LaudoImpressao, LogAuditoria
)

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# remove o admin padrão
admin.site.unregister(User)

# --- 1. CONFIGURAÇÕES ESPECIAIS (CLASSES ADMIN CUSTOMIZADAS) ---

class LogAuditoriaAdmin(admin.ModelAdmin):
    """
    [ALUNO 2] Configuração para o Log de Auditoria: Apenas LEITURA (RDC 330).
    Garante que o passado não possa ser alterado ou forjado.
    """
    list_display = ('data_hora', 'usuario', 'acao', 'ip_origem', 'recurso')
    list_filter = ('acao', 'usuario')
    search_fields = ('usuario__username', 'detalhe')
    readonly_fields = ('data_hora', 'usuario', 'acao', 'recurso', 'detalhe', 'ip_origem', 'protegido')

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class LaudoAdmin(admin.ModelAdmin):
    """
    [ALUNOS 9 e 10] Configuração do Laudo: Layout Dinâmico, Assinatura e Exportação.
    """

    # Colunas da listagem
    list_display = ('id', 'get_paciente', 'analise_info', 'profissional_nome', 'data_hora_emissao', 'link_pdf')

    # Filtros laterais
    list_filter = (
        'data_hora_emissao',
    )

    # Campo de busca
    search_fields = (
    'codigo_verificacao',
    )

    date_hierarchy = 'data_hora_emissao'
    ordering = ('-data_hora_emissao',)

    # [ALUNO 10] Bloqueia upload manual. O sistema gera o arquivo automaticamente.
    readonly_fields = ('caminho_pdf', 'data_hora_emissao')

    # Organização do formulário
    fieldsets = (
        ('Informações do Laudo', {
            'fields': (
                'analise',
                'usuario_responsavel',
                'codigo_verificacao',
            )
        }),
        ('Arquivo PDF', {
            'fields': (
                'caminho_pdf',
            )
        }),
        ('Informações do Sistema', {
            'fields': (
                'data_hora_emissao',
            ),
            'classes': ('collapse',)
        }),
    )

    def analise_info(self, obj):
        try:
            return f"Análise #{obj.analise.id}"
        except AttributeError:
            return "-"
    analise_info.short_description = "Análise de Origem"
    
    def get_paciente(self, obj):
        try:
            return obj.analise.imagem.paciente.nome_completo
        except AttributeError:
            return "-"
    get_paciente.short_description = "Paciente"

    def profissional_nome(self, obj):
        if obj.usuario_responsavel and obj.usuario_responsavel.usuario:
            return obj.usuario_responsavel.usuario.get_full_name() or obj.usuario_responsavel.usuario.username
        return "-"
    profissional_nome.short_description = "Profissional Responsável"

    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario_responsavel__usuario=request.user)

    # [ALUNO 10] Implementação do Preview do Laudo na Interface
    def link_pdf(self, obj):
        if obj.caminho_pdf:
            # Botão Verde: Arquivo existe (Visualização/Preview)
            return format_html(
                '<a class="button" href="{}" target="_blank" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">📄 Ver PDF</a>', 
                obj.caminho_pdf.url
            )
        # Botão Azul: Arquivo inexistente (Ação de Geração/Exportação)
        return format_html(
            '<a class="button" href="gerar/{}/" style="background-color: #007bff; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">⚙️ Gerar PDF</a>', 
            obj.id
        )
    
    link_pdf.short_description = 'Ações do Laudo'

    def get_urls(self):
        """[ALUNO 10] Injeta a rota de geração de PDF na API do Django Admin"""
        urls = super().get_urls()
        custom_urls = [
            path('gerar/<int:laudo_id>/', self.admin_site.admin_view(self.processar_geracao_pdf)),
        ]
        return custom_urls + urls

    def processar_geracao_pdf(self, request, laudo_id):
        """
        [ALUNO 10] Processa a criação física do arquivo.
        [INTEGRAÇÃO] Captura Usuário e IP para os requisitos de Auditoria e Assinatura.
        """
        laudo = self.get_object(request, laudo_id)
        
        # Chama o serviço atualizado com Platypus (Layout Dinâmico)
        ReportService.gerar_pdf_para_laudo_existente(
            laudo_obj=laudo, 
            usuario_solicitante=request.user, 
            ip_cliente=request.META.get('REMOTE_ADDR')
        )
        
        self.message_user(request, f"Sucesso: PDF do Laudo #{laudo_id} foi gerado e assinado digitalmente.")
        return redirect('..')


class PacienteAdmin(admin.ModelAdmin):
    #Configuração do Django Admin para o modelo Paciente

    # Colunas da listagem
    list_display = (
        'nome_completo',
        'cpf',
        'data_nascimento',
        'data_cadastro',
        'uuid_paciente'
    )

    # Filtros laterais
    list_filter = (
        'data_cadastro',
    )

    # Campo de busca
    search_fields = (
        'uuid_paciente',
    )

    # Campos somente leitura
    readonly_fields = (
        'uuid_paciente',
        'data_cadastro',
    )

    # Organização do formulário
    fieldsets = (
        ('Informações Básicas do Paciente', {
            'fields': (
                'nome_completo',
                'cpf',
                'data_nascimento',
            )
        }),
        ('Informações Clínicas', {
            'fields': (
                'sintomas',
                'possivel_diagnostico',
            )
        }),
        ('Informações do Sistema', {
            'fields': (
                'uuid_paciente',
                'data_cadastro',
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'crm',
        'is_staff',
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    def crm(self, obj):
        try:
            return obj.perfilusuario.registro_profissional
        except PerfilUsuario.DoesNotExist:
            return "-"
    crm.short_description = "CRM"

# --- 2. REGISTRO DOS MODELOS NO SISTEMA ---

# Modelos com inteligência administrativa personalizada
admin.site.register(LogAuditoria, LogAuditoriaAdmin)
admin.site.register(Laudo, LaudoAdmin)
admin.site.register(Paciente, PacienteAdmin)

# Modelos com registro simples (Interface padrão Django)
admin.site.register([
    AnaliseImagem,
    HistoricoLaudo,
    ImagemExame,
    Instituicao,
    PerfilUsuario,
    LaudoImpressao
])

# --- NOTAS DO DESENVOLVIMENTO ---
# Luciano e Duda: Estrutura pronta para validação de CPF e Uploads de Imagens.
# Grupo 5: Requisitos de PDF, Assinatura e Rastreabilidade concluídos.