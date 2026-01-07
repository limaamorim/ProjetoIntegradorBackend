from io import BytesIO
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from nucleo.models import Laudo, LaudoImpressao # Modelos do núcleo 
from ..utils.pdf_base import aplicar_estilo_laudo

class ReportService:
    @staticmethod
    def gerar_e_registrar(analise_obj, medico_perfil, ip_cliente):
        # 1. Cria o registro do Laudo (Aluno 10) 
        novo_laudo = Laudo.objects.create(
            analise=analise_obj,
            usuario_responsavel=medico_perfil,
            texto_laudo_completo="Resultado da Análise IA concluído.",
            ip_emissao=ip_cliente,
            confirmou_concordancia=True
        )

        # 2. Gera o PDF em memória (Aluno 9/10) 
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        aplicar_estilo_laudo(p, analise_obj.imagem.instituicao.nome_instituicao)
        p.showPage()
        p.save()
        
        # 3. Registra na área de "Laudo impressaos" 
        LaudoImpressao.objects.create(
            laudo=novo_laudo,
            usuario=medico_perfil.usuario,
            ip_origem=ip_cliente
        )
        
        return novo_laudo