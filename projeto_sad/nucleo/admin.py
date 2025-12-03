from django.contrib import admin
from .models import (
    Instituicao, PerfilUsuario, Paciente, ImagemExame, 
    AnaliseImagem, Laudo, HistoricoLaudo, LaudoImpressao, LogAuditoria
)

# --- Configuração para o Log de Auditoria ---
# Queremos que o Log seja apenas para LEITURA (ninguém pode apagar ou mudar a história)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'acao', 'ip_origem', 'recurso') # Mostra colunas úteis na tela, não só "Log object (1)"
    list_filter = ('acao', 'usuario') # Filtros laterais -Dá pra filtrar só "LOGIN_FALHA" ou só ações do usuário "João".
    search_fields = ('usuario__username', 'detalhe') # Barra de busca - (tipo Google) para procurar por detalhes.
    readonly_fields = ('data_hora', 'usuario', 'acao', 'recurso', 'detalhe', 'ip_origem', 'protegido') # RDC 330: readonly_fields: Ninguém pode editar um log. O que aconteceu, aconteceu.

    # has_add_permission = False: Ninguém pode forjar um log falso.
    def has_add_permission(self, request):
        return False
    
    # has_delete_permission = False: Ninguém pode apagar o passado.
    # Se um hacker invadir ou um médico errar, o rastro fica lá para sempre.
    def has_delete_permission(self, request, obj=None):
        return False

# --- Registro Simples das Outras Tabelas ---
admin.site.register(Instituicao)
admin.site.register(PerfilUsuario)
admin.site.register(Paciente)
admin.site.register(ImagemExame)
admin.site.register(AnaliseImagem)
admin.site.register(Laudo)
admin.site.register(HistoricoLaudo)
admin.site.register(LaudoImpressao)
admin.site.register(LogAuditoria, LogAuditoriaAdmin) # Usa a configuração especial

#Luciano e Duda - Como já ta criado Admin já pode entrar e cadastrar um Paciente manualmente pra ver se o CPF trava.
#e Duda já consegue fazer upload de uma imagem por lá pra ver se salva na pasta certa. :)
