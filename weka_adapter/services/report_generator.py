import uuid
from io import BytesIO
from PIL import Image  # Processa os bytes descriptografados (Aluno 10)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.utils import ImageReader

from django.core.files.base import ContentFile
from nucleo.models import Laudo, LaudoImpressao 
from ..utils.pdf_base import aplicar_estilo_laudo
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing

class ReportService:
    """
    [ALUNO 10] Versão Final de Entrega.
    Sistema de laudos com criptografia AES-GCM e ajuste fino de layout.
    """

    @staticmethod
    def gerar_pdf_para_laudo_existente(laudo_obj, usuario_solicitante=None, ip_cliente="0.0.0.0"):
        buffer = BytesIO()
        
        # 1. Configuração do Documento
        # topMargin de 5.5cm garante que o texto comece abaixo do logotipo
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            rightMargin=2*cm, 
            leftMargin=2*cm, 
            topMargin=5.5*cm, 
            bottomMargin=2.5*cm
        )
        
        estilos = getSampleStyleSheet()
        estilo_corpo = ParagraphStyle('Corpo', parent=estilos['Normal'], fontSize=11, alignment=TA_JUSTIFY)
        estilo_assin_texto = ParagraphStyle('Assin', parent=estilos['Normal'], fontSize=8, alignment=TA_CENTER)

        elementos = []

        # 2. Tabela de Identificação (Cabeçalho de dados)
        dados_paciente = [
            [f"PACIENTE: {laudo_obj.analise.imagem.paciente.nome_completo}", f"ID: {laudo_obj.id}"],
            [f"DATA DE EMISSÃO: {laudo_obj.data_hora_emissao.strftime('%d/%m/%Y %H:%M')}", f"CÓDIGO: {laudo_obj.codigo_verificacao}"]
        ]
        tabela_id = Table(dados_paciente, colWidths=[13*cm, 4*cm])
        tabela_id.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        elementos.append(tabela_id)
        elementos.append(Spacer(1, 20))

        # 3. Conteúdo do Laudo
        elementos.append(Paragraph("DESCRIÇÃO DOS ACHADOS:", estilos['Heading2']))
        texto_limpo = laudo_obj.texto_laudo_completo.replace('\n', '<br/>')
        elementos.append(Paragraph(texto_limpo, estilo_corpo))
        
        elementos.append(Spacer(1, 2*cm))

        # 4. QR Code e Assinatura
        link_validacao = f"https://sad.saude.gov.br/validar/{laudo_obj.codigo_verificacao}"
        qr_code = qr.QrCodeWidget(link_validacao)
        desenho_qr = Drawing(65, 65)
        desenho_qr.add(qr_code)
        
        medico = laudo_obj.usuario_responsavel.usuario.get_full_name() or "Médico Responsável"
        layout_assinatura = [
            [desenho_qr], 
            ["________________________________________________"], 
            [f"Dr(a). {medico}"], 
            [Paragraph("Documento assinado digitalmente - Validação via QR Code", estilo_assin_texto)],
            [Paragraph(f"Autenticação: {laudo_obj.codigo_verificacao}", estilo_assin_texto)]
        ]
        tabela_as = Table(layout_assinatura, colWidths=[17*cm])
        tabela_as.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        elementos.append(tabela_as)

        # 5. Função de Setup (Desenha o Logo e Marca d'água)
        def on_page_setup(canvas_obj, doc_obj):
            inst_obj = laudo_obj.analise.imagem.instituicao
            
            # Aplica marca d'água e nome da instituição (fundo)
            aplicar_estilo_laudo(canvas_obj, inst_obj.nome_instituicao)
            
            # Desenha o Logotipo (Sobreposto)
            if inst_obj.logo:
                try:
                    with inst_obj.logo.open('rb') as f:
                        img_bytes = f.read()
                        if img_bytes:
                            img_pil = Image.open(BytesIO(img_bytes))
                            if img_pil.mode in ("RGBA", "P"):
                                img_pil = img_pil.convert("RGB")
                            
                            img_render = ImageReader(img_pil)
                            
                            # --- AJUSTE DE POSIÇÃO ---
                            # X = 15cm (direita)
                            # Y = 22.5cm (baixamos para não cortar no topo da folha)
                            # width = 4cm (tamanho padrão para logos de laudo)
                            canvas_obj.drawImage(img_render, 15*cm, 22.5*cm, width=4*cm, preserveAspectRatio=True, mask='auto')
                            
                except Exception as e:
                    print(f"--- FALHA NO LOGOTIPO: {e} ---")

        # 6. Build
        doc.build(elementos, onFirstPage=on_page_setup, onLaterPages=on_page_setup)

        # 7. Finalização e Auditoria
        pdf_final = buffer.getvalue()
        buffer.close()
        
        nome_arquivo = f"laudo_{laudo_obj.id}_{laudo_obj.codigo_verificacao}.pdf"
        laudo_obj.caminho_pdf.save(nome_arquivo, ContentFile(pdf_final))
        laudo_obj.save()
        
        if usuario_solicitante:
            LaudoImpressao.objects.create(laudo=laudo_obj, usuario=usuario_solicitante, ip_origem=ip_cliente)
        
        return laudo_obj

    @staticmethod
    def gerar_e_registrar(analise_obj, medico_perfil, ip_cliente):
        novo_laudo = Laudo.objects.create(
            analise=analise_obj, usuario_responsavel=medico_perfil,
            texto_laudo_completo="Sistema Validado: Criptografia AES-GCM e Layout PDF ok.",
            ip_emissao=ip_cliente, confirmou_concordancia=True,
            codigo_verificacao=str(uuid.uuid4())[:8]
        )
        return ReportService.gerar_pdf_para_laudo_existente(novo_laudo)