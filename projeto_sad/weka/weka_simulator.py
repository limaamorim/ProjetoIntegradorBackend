"""
weka/weka_simulator.py
Simulador principal do WEKA - Faz a "classificação"
Aluno 7: Especialista WEKA (Núcleo da simulação)
"""

import random
import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class WekaSimulator:
    """
    Simula o comportamento do WEKA (ferramenta de machine learning).
    """
    
    def __init__(self):
        self.classes = ['NORMAL', 'BENIGNO', 'CISTO', 'MALIGNO']
    
    def classify(self, features: List[float]) -> Dict:
        """
        Simula a classificação de uma imagem termográfica.
        
        Args:
            features: Lista de 9 características da imagem
            
        Returns:
            Dicionário com resultado da classificação
        """
        logger.info("[WEKA SIMULATOR] Iniciando classificação simulada")
        
        # Simular tempo de processamento
        time.sleep(0.1)  # Pequena pausa para parecer real
        
        # Analisar características para decidir diagnóstico
        if len(features) >= 9:
            temperatura_media = features[0]
            assimetria = features[8]
        else:
            # Valores padrão se features incompletas
            temperatura_media = 37.0
            assimetria = 0.5
        
        # Lógica de decisão simulada
        if temperatura_media < 36.8 and assimetria < 0.3:
            predicted_class = 'NORMAL'
            confidence = random.uniform(85, 95)
        elif temperatura_media < 37.3:
            predicted_class = 'BENIGNO'
            confidence = random.uniform(75, 90)
        elif temperatura_media < 37.8:
            predicted_class = 'CISTO'
            confidence = random.uniform(70, 85)
        else:
            predicted_class = 'MALIGNO'
            confidence = random.uniform(65, 80)
        
        # Gerar probabilidades
        probs = self._generate_probabilities(predicted_class, confidence)
        
        # Criar saída no formato WEKA
        class_index = self.classes.index(predicted_class) + 1
        weka_output = f"1: ? {class_index}:{predicted_class} {','.join([f'{p:.3f}' for p in probs])}"
        
        return {
            'success': True,
            'predicted_class': predicted_class,
            'confidence_percentage': round(confidence, 2),
            'probabilities': probs,
            'raw_weka_output': weka_output,
            'simulation_mode': True
        }
    
    def _generate_probabilities(self, predicted_class: str, confidence: float) -> List[float]:
        """Gera probabilidades realistas."""
        confidence_decimal = confidence / 100
        remaining = 1.0 - confidence_decimal
        other_classes = len(self.classes) - 1
        
        probabilities = []
        for cls in self.classes:
            if cls == predicted_class:
                probabilities.append(round(confidence_decimal, 4))
            else:
                probabilities.append(round(remaining / other_classes, 4))
        
        # Ajustar soma para 1.0
        total = sum(probabilities)
        if total != 1.0:
            probabilities[-1] = round(probabilities[-1] + (1.0 - total), 4)
        
        return probabilities

# Função de conveniência
def classify_with_weka(features: List[float]) -> Dict:
    """Função simples para classificação."""
    simulator = WekaSimulator()
    return simulator.classify(features)
