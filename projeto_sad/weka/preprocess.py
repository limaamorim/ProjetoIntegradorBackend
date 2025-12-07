"""
weka/preprocess.py
Módulo de pré-processamento SIMULADO para imagens termográficas
Aluno 7: Especialista WEKA (Modo Simulado)
"""

import numpy as np
import os
import hashlib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def extract_features_from_image(image_path):
    """
    Simula a extração de características de uma imagem termográfica.
    
    EM UM SISTEMA REAL: Aqui usaríamos OpenCV/NumPy para analisar a imagem.
    NO SIMULADOR: Geramos características baseadas no nome/arquivo.
    
    Args:
        image_path: Caminho para a imagem (qualquer imagem .jpg/.png serve)
        
    Returns:
        Lista com 9 características numéricas simuladas
    """
    logger.info(f"[WEKA SIMULADO] Extraindo características de: {image_path}")
    
    # 1. Pegar informações do arquivo para gerar dados consistentes
    filename = os.path.basename(image_path).lower()
    
    # 2. Usar hash do nome para gerar números "pseudo-aleatórios consistentes"
    file_hash = hashlib.md5(filename.encode()).hexdigest()
    hash_int = int(file_hash[:8], 16)  # Converter parte do hash para número
    
    # 3. Gerar características baseadas no nome do arquivo (para testes consistentes)
    if 'normal' in filename or 'saudavel' in filename:
        # Padrão para casos normais
        base_temp = 36.5 + (hash_int % 100) / 1000  # 36.5-36.6
        base_variation = 0.3 + (hash_int % 70) / 100  # 0.3-1.0
    elif 'benigno' in filename:
        base_temp = 37.0 + (hash_int % 150) / 1000  # 37.0-37.15
        base_variation = 0.8 + (hash_int % 120) / 100  # 0.8-2.0
    elif 'cisto' in filename:
        base_temp = 37.5 + (hash_int % 200) / 1000  # 37.5-37.7
        base_variation = 1.2 + (hash_int % 180) / 100  # 1.2-3.0
    elif 'maligno' in filename:
        base_temp = 38.0 + (hash_int % 300) / 1000  # 38.0-38.3
        base_variation = 1.5 + (hash_int % 250) / 100  # 1.5-4.0
    else:
        # Padrão genérico
        base_temp = 37.2 + (hash_int % 200) / 1000  # 37.2-37.4
        base_variation = 1.0 + (hash_int % 150) / 100  # 1.0-2.5
    
    # 4. Gerar as 9 características
    features = [
        round(base_temp, 2),                           # 1. Temperatura média
        round(base_variation, 2),                      # 2. Desvio padrão
        round(base_temp - 0.5, 2),                     # 3. Percentil 25%
        round(base_temp + 0.5, 2),                     # 4. Percentil 75%
        round(base_temp + 1.0, 2),                     # 5. Temperatura máxima
        round(base_temp - 1.0, 2),                     # 6. Temperatura mínima
        round(base_temp, 2),                           # 7. Temperatura mediana
        round(base_variation ** 2, 4),                 # 8. Variância
        round(base_variation * 0.8, 2)                 # 9. Assimetria térmica
    ]
    
    logger.debug(f"Características simuladas: {features}")
    return features

def create_arff_content(features, class_label="?"):
    """
    Cria conteúdo no formato ARFF (formato que o WEKA entende).
    
    EM UM SISTEMA REAL: Este arquivo seria enviado ao WEKA Java.
    NO SIMULADOR: Apenas criamos o formato para demonstração.
    
    Args:
        features: Lista de 9 características
        class_label: Classe do diagnóstico ou "?" para predição
        
    Returns:
        String com conteúdo ARFF formatado
    """
    # Cabeçalho do arquivo ARFF
    arff_header = f"""@RELATION termografia_mamaria_simulada

@ATTRIBUTE temperatura_media NUMERIC
@ATTRIBUTE desvio_padrao NUMERIC
@ATTRIBUTE percentil_25 NUMERIC
@ATTRIBUTE percentil_75 NUMERIC
@ATTRIBUTE temperatura_max NUMERIC
@ATTRIBUTE temperatura_min NUMERIC
@ATTRIBUTE temperatura_mediana NUMERIC
@ATTRIBUTE variancia NUMERIC
@ATTRIBUTE assimetria_termica NUMERIC
@ATTRIBUTE classe {{{','.join(settings.WEKA_CLASSES)}}}

@DATA
"""
    
    # Formatar características com 4 casas decimais
    features_str = ",".join([f"{f:.4f}" for f in features])
    
    # Combinar tudo
    return arff_header + features_str + "," + class_label + "\n"

def save_features_to_tempfile(features, class_label="?"):
    """
    Salva características em um arquivo temporário ARFF.
    Útil para demonstração e logs.
    """
    import tempfile
    
    arff_content = create_arff_content(features, class_label)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.arff', delete=False) as f:
        f.write(arff_content)
        temp_path = f.name
    
    logger.info(f"Arquivo ARFF temporário criado: {temp_path}")
    return temp_path
