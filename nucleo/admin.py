from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.http import HttpResponse
from io import BytesIO
import zipfile
import os
from django.utils import timezone
from nucleo.auditoria import audit_log

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

admin.site.site_title = 'Administração do Sistema' 
admin.site.index_title = 'Bem-vindo ao Painel de Controle' 

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

    actions = ['gerar_pdfs_zip']

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

        audit_log(
            request=request,
            acao="LAUDO_IMPRESSO",
            recurso="PDF Laudo",
            detalhe=f"laudo_id={laudo_id} codigo={getattr(laudo,'codigo_verificacao',None)}",
        )
        
        self.message_user(request, f"Sucesso: PDF do Laudo #{laudo_id} foi gerado e assinado digitalmente.")
        return redirect('..')
    
    def save_model(self, request, obj, form, change):
        is_create = obj.pk is None
        super().save_model(request, obj, form, change)

        audit_log(
            request=request,
            acao="LAUDO_GERADO" if is_create else "LAUDO_ALTERADO",
            recurso="Laudo",
            detalhe=f"id={obj.id} codigo={getattr(obj,'codigo_verificacao',None)}",
        )
    
    # Gera laudos massivamente
    def gerar_pdfs_zip(self, request, queryset):
        """
        Ação em massa: gera PDFs dos laudos selecionados, devolve um ZIP e inclui
        um relatorio_exportacao.txt com detalhes (sucessos/falhas).
        Registra log de auditoria ao final.
        """

        # RBAC: usuário comum só exporta laudos do próprio PerfilUsuario->User
        if not request.user.is_superuser:
            queryset = queryset.filter(usuario_responsavel__usuario=request.user)

        total_selecionados = queryset.count()
        exportados = 0
        falhas = 0

        # Relatório em texto (vai virar um .txt dentro do ZIP)
        linhas_relatorio = []
        linhas_relatorio.append("RELATÓRIO DE EXPORTAÇÃO DE LAUDOS (ZIP)")
        linhas_relatorio.append(f"Data/Hora: {timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        linhas_relatorio.append(f"Usuário: {request.user.username}")
        linhas_relatorio.append(f"IP: {request.META.get('REMOTE_ADDR')}")
        linhas_relatorio.append(f"Total selecionados (após RBAC): {total_selecionados}")
        linhas_relatorio.append("-" * 60)

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for laudo in queryset:
                codigo = getattr(laudo, "codigo_verificacao", None) or f"id_{laudo.id}"

                try:
                    # Gera PDF se não existir
                    if not laudo.caminho_pdf:
                        ReportService.gerar_pdf_para_laudo_existente(
                            laudo_obj=laudo,
                            usuario_solicitante=request.user,
                            ip_cliente=request.META.get("REMOTE_ADDR"),
                        )
                        laudo.refresh_from_db(fields=["caminho_pdf", "codigo_verificacao"])

                    if not laudo.caminho_pdf:
                        falhas += 1
                        linhas_relatorio.append(f"[FALHA] Laudo {codigo}: caminho_pdf vazio após tentativa de geração.")
                        continue

                    caminho = laudo.caminho_pdf.path
                    if not os.path.exists(caminho):
                        falhas += 1
                        linhas_relatorio.append(f"[FALHA] Laudo {codigo}: arquivo não encontrado em disco ({caminho}).")
                        continue

                    nome_no_zip = f"laudo_{codigo}.pdf"
                    zip_file.write(caminho, arcname=nome_no_zip)
                    exportados += 1
                    linhas_relatorio.append(f"[OK] Laudo {codigo}: adicionado como {nome_no_zip}")

                except Exception as e:
                    falhas += 1
                    linhas_relatorio.append(f"[ERRO] Laudo {codigo}: {type(e).__name__} - {e}")

            linhas_relatorio.append("-" * 60)
            linhas_relatorio.append(f"Exportados com sucesso: {exportados}")
            linhas_relatorio.append(f"Falhas: {falhas}")

            # Escreve o TXT dentro do ZIP
            conteudo_txt = "\n".join(linhas_relatorio)
            zip_file.writestr("relatorio_exportacao.txt", conteudo_txt)

        # Log de auditoria (um único registro)
        LogAuditoria.objects.create(
            usuario=request.user,
            acao="LAUDO_IMPRESSO",  # ou 'EXPORTACAO_LAUDOS' se você adicionar esse tipo no model
            recurso="Exportação em Massa de Laudos",
            detalhe=f"Selecionados: {total_selecionados} | Exportados: {exportados} | Falhas: {falhas}",
            ip_origem=request.META.get("REMOTE_ADDR"),
        )

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="laudos_selecionados.zip"'
        return response

    gerar_pdfs_zip.short_description = "Gerar PDFs (ZIP) + relatório TXT"



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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        audit_log(
            request=request,
            acao="PACIENTE_ATUALIZADO" if change else "PACIENTE_CRIADO",
            recurso="Paciente",
            detalhe=f"paciente_uuid={obj.uuid_paciente}",
        )

    def delete_model(self, request, obj):
        uuid_val = obj.uuid_paciente

        audit_log(
            request=request,
            acao="PACIENTE_EXCLUIDO",
            recurso="Paciente",
            detalhe=f"paciente_uuid={uuid_val}",
        )

        super().delete_model(request, obj)

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