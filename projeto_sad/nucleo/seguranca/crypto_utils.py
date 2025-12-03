"""
Funções utilitárias para criptografia AES-256 GCM.

Responsabilidades:
- Converter valores em bytes
- Criptografar (encrypt_value)
- Descriptografar (decrypt_value)
- Retornar valores como strings base64 para armazenamento seguro no SQLite
"""

import base64
from django.conf import settings
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Tamanho padrão recomendado para AES-GCM
NONCE_SIZE = 12
TAG_SIZE = 16


def encrypt_value(value: str) -> str:
    """
    Criptografa um valor textual usando AES-256 GCM.
    
    Retorna: string base64 (nonce + ciphertext + tag)
    """
    if value is None:
        return None

    # Se for string, converte para bytes
    if not isinstance(value, bytes):
        value = value.encode()

    # Gera nonce único para cada criptografia
    nonce = get_random_bytes(NONCE_SIZE)

    # AES-256 GCM
    cipher = AES.new(settings.AES_KEY, AES.MODE_GCM, nonce=nonce)

    # Criptografa + gera tag de integridade
    ciphertext, tag = cipher.encrypt_and_digest(value)

    # Monta pacote final
    payload = nonce + ciphertext + tag

    # Armazena em base64 como string
    return base64.b64encode(payload).decode()


def decrypt_value(value: str) -> str:
    """
    Descriptografa valores produzidos por encrypt_value.
    
    Espera receber string base64.
    """
    if value is None:
        return None

    # Converte base64 para bytes
    payload = base64.b64decode(value.encode())

    # Reconstruct payload
    nonce = payload[:NONCE_SIZE]
    tag = payload[-TAG_SIZE:]
    ciphertext = payload[NONCE_SIZE:-TAG_SIZE]

    cipher = AES.new(settings.AES_KEY, AES.MODE_GCM, nonce=nonce)

    # Verifica tag e descriptografa
    data = cipher.decrypt_and_verify(ciphertext, tag)

    return data.decode()
