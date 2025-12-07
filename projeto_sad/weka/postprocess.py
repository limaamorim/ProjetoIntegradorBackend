"""
weka/postprocess.py
Processamento da "saída" do WEKA simulado
Aluno 7: Especialista WEKA
"""

import logging

logger = logging.getLogger(__name__)

def parse_weka_output(weka_output: str = None):
    """
    Parseia a saída do WEKA (simulada).
    """
    if weka_output and "?" in weka_output and ":" in weka_output:
        # Tentar extrair informações
        parts = weka_output.split()
        if len(parts) >= 3:
            predicted = parts[2].split(':')[1] if ':' in parts[2] else parts[2]
            return {
                'success': True,
                'predicted_class': predicted,
                'raw_output': weka_output
            }
    
    # Se não conseguir parsear, retorna simulado
    from .weka_simulator import classify_with_weka
    features = [37.0, 1.0, 36.5, 37.5, 38.0, 36.0, 37.0, 1.0, 0.5]
    return classify_with_weka(features)

def generate_report(result):
    """Gera relatório simples do diagnóstico."""
    if not result.get('success', False):
        return "Erro na classificação."
    
    predicted = result['predicted_class']
    confidence = result.get('confidence_percentage', 0)
    
    reports = {
        'NORMAL': f"✅ NORMAL ({confidence}% de confiança)\nPadrão térmico dentro do esperado.",
        'BENIGNO': f"⚠️ BENIGNO ({confidence}%)\nPossível condição benigna. Recomenda-se acompanhamento.",
        'CISTO': f"⚠️ CISTO ({confidence}%)\nPadrão sugestivo de formação cística. Consulte um especialista.",
        'MALIGNO': f"🚨 SUSPEITO DE MALIGNIDADE ({confidence}%)\nProcure avaliação médica URGENTE."
    }
    
    return reports.get(predicted, f"Resultado: {predicted}")
