from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
import os

from .models import Laudo, LogAuditoria, LaudoImpressao


def gerar_laudo_pdf(request, laudo_id):
    laudo = get_object_or_404(Laudo, id=laudo_id)

    pasta = os.path.join(settings.MEDIA_ROOT, 'laudos')
    os.makedirs(pasta, exist_ok=True)

    nome = f"laudo_{laudo.codigo_verificacao}.pdf"
    caminho = os.path.join(pasta, nome)

    c = canvas.Canvas(caminho, pagesize=A4)
    w, h = A4
    y = h - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "LAUDO MÉDICO OFICIAL")
    y -= 30

    paciente = laudo.analise.imagem.paciente
    analise = laudo.analise

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Paciente: {paciente.nome_completo}")
    y -= 15
    c.drawString(50, y, f"Resultado: {analise.resultado_classificacao}")
    y -= 15
    c.drawString(50, y, f"Score IA: {analise.score_confianca}")
    y -= 20

    text = c.beginText(50, y)
    for linha in laudo.texto_laudo_completo.split('\n'):
        text.textLine(linha)

    c.drawText(text)
    c.showPage()
    c.save()

    laudo.caminho_pdf = f"laudos/{nome}"
    laudo.save(update_fields=['caminho_pdf'])

    LaudoImpressao.objects.create(
        laudo=laudo,
        usuario=request.user,
        ip_origem=request.META.get('REMOTE_ADDR')
    )

    LogAuditoria.objects.create(
        usuario=request.user,
        acao='LAUDO_IMPRESSO',
        recurso='PDF Laudo',
        detalhe=laudo.codigo_verificacao,
        ip_origem=request.META.get('REMOTE_ADDR')
    )

    response = HttpResponse(open(caminho, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nome}"'
    return response
