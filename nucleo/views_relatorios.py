from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date

from .models import Laudo, LogAuditoria


class RelatorioLaudosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        inicio = parse_date(request.GET.get('inicio'))
        fim = parse_date(request.GET.get('fim'))

        qs = Laudo.objects.all()

        if inicio and fim:
            qs = qs.filter(data_hora_emissao__date__range=[inicio, fim])

        dados = []
        for laudo in qs:
            dados.append({
                "paciente": str(laudo.analise.imagem.paciente.nome_completo),
                "resultado": laudo.analise.resultado_classificacao,
                "data": laudo.data_hora_emissao
            })

        LogAuditoria.objects.create(
            usuario=request.user,
            acao='ACESSO_RELATORIO',
            recurso='Relatório de Laudos',
            ip_origem=request.META.get('REMOTE_ADDR')
        )

        return Response(dados)
