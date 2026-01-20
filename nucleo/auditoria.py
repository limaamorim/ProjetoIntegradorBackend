"""
Este módulo centraliza toda a lógica de REGISTRO DE AUDITORIA do sistema.

Objetivo:
- Garantir rastreabilidade completa das ações executadas no sistema
- Garantir a reutilização do código de auditoria
- Atender aos requisitos de conformidade da RDC 330 / ANVISA

Este arquivo NÃO contém regras de negócio, ele registra eventos relevantes de forma padronizada.
"""

from .models import LogAuditoria

def get_ip(request):
    if not request:
        return "0.0.0.0"
    return request.META.get("REMOTE_ADDR") or "0.0.0.0"

def audit_log(*, request=None, usuario=None, acao, recurso=None, detalhe=None):
    if usuario is None and request and getattr(request, "user", None) and request.user.is_authenticated:
        usuario = request.user

    LogAuditoria.objects.create(
        usuario=usuario,
        acao=acao,
        recurso=recurso,
        detalhe=detalhe,
        ip_origem=get_ip(request),
    )
