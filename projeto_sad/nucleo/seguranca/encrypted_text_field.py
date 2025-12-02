"""
Campo de texto longo criptografado (AES-256 GCM).
Ideal para laudos, logs ou qualquer texto sensível.
"""

from django.db import models
from .crypto_utils import encrypt_value, decrypt_value


class EncryptedTextField(models.TextField):
    """TextField criptografado automaticamente."""

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return decrypt_value(value)

    def get_prep_value(self, value):
        if value is None:
            return None
        return encrypt_value(value)
