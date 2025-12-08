"""
weka_adapter/__init__.py
Adaptador WEKA para sistema de classificação de imagens termográficas
Aluno 8: Adaptador WEKA

Este pacote fornece:
- WekaAdapter: Comunicação com WEKA via linha de comando
- WekaClassificationService: Serviço de classificação de imagens
- API REST: Endpoints para classificação via web
"""

__version__ = '1.0.0'
__author__ = 'Aluno 8'
__description__ = 'Adaptador WEKA para classificação de imagens termográficas'

# Importações principais para facilitar acesso
from .adapters import WekaAdapter
from .services import WekaClassificationService

# Versão simplificada para importação direta
__all__ = [
    'WekaAdapter',
    'WekaClassificationService',
]

# Configuração de logging
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
