"""

Este módulo implementa sinais do Django (signals) para registrar eventos
de auditoria de forma AUTOMÁTICA, sem acoplamento às views ou serviços.

Objetivo:
- Garantir que ações críticas sejam auditadas mesmo sem o desenvolvedor chamar explicitamente o audit_log
- Reforçar a conformidade com requisitos regulatórios (RDC 330)
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .auditoria import audit_log

@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    audit_log(request=request, usuario=user, acao="LOGIN_SUCESSO", recurso="Auth", detalhe="Login")

@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    audit_log(request=request, usuario=user, acao="LOGOUT", recurso="Auth", detalhe="Logout")

@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get("username") if credentials else None
    audit_log(request=request, usuario=None, acao="LOGIN_FALHA", recurso="Auth", detalhe=f"username={username}")
