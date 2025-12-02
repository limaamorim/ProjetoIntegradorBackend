"""
Campo de arquivo que usa o EncryptedStorage.
Todos os uploads são criptografados automaticamente.
"""

from django.db.models import FileField
from .encrypted_storage import EncryptedStorage


class EncryptedFileField(FileField):
    """FileField com criptografia AES-256 automática via EncryptedStorage."""

    def __init__(self, *args, **kwargs):
        # Força o uso do storage criptografado
        kwargs["storage"] = EncryptedStorage()
        super().__init__(*args, **kwargs)
