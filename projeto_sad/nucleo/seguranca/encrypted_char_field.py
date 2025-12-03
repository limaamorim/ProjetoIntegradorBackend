"""
Campo de texto curto criptografado usando AES-256 (GCM).
Armazena valores como base64 no banco.
"""

from django.db import models
from .crypto_utils import encrypt_value, decrypt_value


class EncryptedCharField(models.CharField):
    """
    Campo similar ao CharField, porém criptografa automaticamente
    antes de salvar e descriptografa ao ler do banco.
    """

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_value(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return encrypt_value(value)
