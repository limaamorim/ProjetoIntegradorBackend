from .auditoria import audit_log

class AuditoriaErroMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            audit_log(
                request=request,
                acao="ERRO_SISTEMA",
                recurso="Middleware",
                detalhe=f"{type(e).__name__}: {e} | path={request.path}",
            )
            raise
