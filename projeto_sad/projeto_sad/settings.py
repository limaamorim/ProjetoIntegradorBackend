# ====================================================================
# CONFIGURAÇÕES WEKA (Aluno 7 - Especialista WEKA)
# ====================================================================

# Modo de operação
WEKA_MODE = 'simulado'  # 'simulado' ou 'real'

# Classes de diagnóstico suportadas
WEKA_CLASSES = ['NORMAL', 'BENIGNO', 'CISTO', 'MALIGNO']

# Configurações do simulador
WEKA_SIMULATOR = {
    'confidence_min': 70,
    'confidence_max': 95,
    'processing_time_min': 0.5,
    'processing_time_max': 2.0,
}

# ====================================================================
# CONFIGURAÇÕES WEKA ADAPTER (Aluno 8 - Adaptador WEKA)
# ====================================================================

# Caminho para o executável Java/WEKA
WEKA_JAVA_PATH = 'java'

# Caminho para o arquivo JAR do WEKA (se não estiver no classpath)
WEKA_JAR_PATH = os.path.join(BASE_DIR, 'weka', 'weka.jar')

# Classificador a ser usado
WEKA_CLASSIFIER = 'weka.classifiers.trees.RandomForest'

# Parâmetros do classificador
WEKA_CLASSIFIER_PARAMS = ['-I', '100', '-K', '0', '-S', '1']

# Caminho para dados do WEKA
WEKA_DATA_DIR = os.path.join(BASE_DIR, 'weka', 'weka_data')

# Criar diretório se não existir
os.makedirs(WEKA_DATA_DIR, exist_ok=True)

# Caminho completo para o modelo ⭐ APENAS ESTA LINHA!
WEKA_MODEL_PATH = os.path.join(WEKA_DATA_DIR, 'randomforest.model')

# Caminho para arquivos ARFF temporários
WEKA_TEMP_DIR = os.path.join(BASE_DIR, 'temp', 'weka')
os.makedirs(WEKA_TEMP_DIR, exist_ok=True)

# Configurações de logging para WEKA
WEKA_LOG_LEVEL = 'INFO'

# Timeout para execução do WEKA (em segundos)
WEKA_TIMEOUT = 30

# Configuração para modo de desenvolvimento
WEKA_FALLBACK_TO_SIMULATED = True
