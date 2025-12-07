"""
weka/apps.py
Configuração do app Django para o módulo WEKA
"""
from django.apps import AppConfig

class WekaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weka'  # diagnostico_weka 
    verbose_name = 'Sistema WEKA Simulado'  # weka_simulador
