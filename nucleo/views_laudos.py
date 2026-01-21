from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Laudo, LogAuditoria



class HistoricoLaudosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        laudos = Laudo.objects.select_related(
            'analise__imagem__paciente',
            'usuario_responsavel'
        ).order_by('-data_hora_emissao')

        resultado = []
        for laudo in laudos:
            resultado.append({
                "id": laudo.id,
                "paciente": str(laudo.analise.imagem.paciente.nome_completo),
                "resultado": laudo.analise.resultado_classificacao,
                "data_emissao": laudo.data_hora_emissao,
                "codigo_verificacao": laudo.codigo_verificacao,
                "pdf": laudo.caminho_pdf
            })

        LogAuditoria.objects.create(
            usuario=request.user,
            acao='ACESSO_RELATORIO',
            recurso='Histórico de Laudos',
            ip_origem=request.META.get('REMOTE_ADDR')
        )

        return Response(resultado)
