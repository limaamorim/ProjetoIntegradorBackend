"""
weka_adapter/apps.py
Configuração da aplicação Django para o Adaptador WEKA
"""
from django.apps import AppConfig


class WekaAdapterConfig(AppConfig):
    """
    Configuração da aplicação WEKA Adapter.
    """
    name = 'weka_adapter'
    verbose_name = 'Adaptador WEKA'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        """
        Código executado quando a aplicação está pronta.
        """
        try:
            # Importações para inicialização
            from .signals import setup_signals  # Se tiver signals
            setup_signals()
        except ImportError:
            pass
        
        # Inicializar logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Aplicação {self.verbose_name} inicializada")
