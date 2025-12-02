"""
Criptografa arquivos binários antes de salvar no disco.

Modo de operação:
- No _save(): criptografa (AES-GCM)
- No _open(): descriptografa
"""

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

NONCE_SIZE = 12
TAG_SIZE = 16


class EncryptedStorage(FileSystemStorage):
    """Armazena arquivos criptografados em disco usando AES-GCM."""

    def _save(self, name, content):
        # Lê bytes do arquivo
        data = content.read()

        # Cria nonce único
        nonce = get_random_bytes(NONCE_SIZE)
        cipher = AES.new(settings.AES_KEY, AES.MODE_GCM, nonce=nonce)

        ciphertext, tag = cipher.encrypt_and_digest(data)

        payload = nonce + ciphertext + tag

        # Re-empacota em arquivo
        from django.core.files.base import ContentFile
        encrypted_file = ContentFile(payload)

        return super()._save(name, encrypted_file)

    def _open(self, name, mode='rb'):
        f = super()._open(name, mode)
        payload = f.read()

        nonce = payload[:NONCE_SIZE]
        tag = payload[-TAG_SIZE:]
        ciphertext = payload[NONCE_SIZE:-TAG_SIZE]

        cipher = AES.new(settings.AES_KEY, AES.MODE_GCM, nonce=nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)

        from django.core.files.base import ContentFile
        return ContentFile(data)
