"""

Este módulo implementa sinais do Django (signals) para registrar eventos
de auditoria de forma AUTOMÁTICA, sem acoplamento às views ou serviços.

Objetivo:
- Garantir que ações críticas sejam auditadas mesmo sem o desenvolvedor chamar explicitamente o audit_log
- Reforçar a conformidade com requisitos regulatórios (RDC 330)
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, post_delete
from .models import Paciente, ImagemExame, Laudo
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


@receiver(post_save, sender=ImagemExame)
def auditar_imagemexame_salvo(sender, instance: ImagemExame, created: bool, **kwargs):
    """
    Auditoria automática para ImagemExame.
    Aqui dá para capturar usuário porque existe o campo usuario_upload no model.
    IP ainda não existe aqui sem request; por isso o IP cairá no default 0.0.0.0
    a menos que você implemente threadlocal middleware.
    """
    audit_log(
        usuario=getattr(instance, "usuario_upload", None),
        acao="UPLOAD_IMAGEM" if created else "ACESSO_RELATORIO",
        recurso="ImagemExame",
        detalhe=(
            f"{'UPLOAD' if created else 'ATUALIZACAO'} imagem_id={instance.id} "
            f"paciente_uuid={instance.paciente.uuid_paciente} instituicao_id={instance.instituicao_id}"
        ),
        request=None,
    )


@receiver(post_delete, sender=ImagemExame)
def auditar_imagemexame_deletado(sender, instance: ImagemExame, **kwargs):
    """
    Auditoria automática para exclusão de ImagemExame.
    """
    audit_log(
        usuario=getattr(instance, "usuario_upload", None),
        acao="ACESSO_RELATORIO",
        recurso="ImagemExame",
        detalhe=f"EXCLUSAO imagem_id={instance.id} paciente_uuid={instance.paciente.uuid_paciente}",
        request=None,
    )