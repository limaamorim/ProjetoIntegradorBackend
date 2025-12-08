"""
weka_adapter/admin.py
Configuração do Admin para o Adaptador WEKA
"""
from django.contrib import admin
from .models import ClassificationResult

# Se você tiver um modelo, registre-o aqui
# admin.site.register(ClassificationResult)

# Ou configure uma página admin personalizada se necessário
class WekaAdminSite(admin.AdminSite):
    site_header = 'WEKA Adapter Admin'
    site_title = 'WEKA Adapter'
    index_title = 'Painel de Administração'

# Se quiser criar um admin personalizado
weka_admin = WekaAdminSite(name='weka_admin')
