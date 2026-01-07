from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

def aplicar_estilo_laudo(canvas_obj, instituicao_nome):
    # Cabeçalho dinâmico (Aluno 9) 
    canvas_obj.setFont("Helvetica-Bold", 14)
    canvas_obj.drawString(2*cm, 28*cm, f"INSTITUIÇÃO: {instituicao_nome}")
    
    # Marca d'água de segurança (Exigência Aluno 9) 
    canvas_obj.saveState()
    canvas_obj.setFillAlpha(0.1)
    canvas_obj.translate(10*cm, 15*cm)
    canvas_obj.rotate(45)
    canvas_obj.drawCentredString(0, 0, "VIA ORIGINAL - PROJETO SAD")
    canvas_obj.restoreState()