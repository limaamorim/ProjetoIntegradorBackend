"""
Django settings for projeto_sad project.
"""
from dotenv import load_dotenv
import base64
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis do .env
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não definida no .env")

DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # APPS DO PROJETO
    'nucleo',
    'simulador',
    'rest_framework',
    'weka',           # App do aluno 7
    'weka_adapter',   # ⭐ SEU APP - Adaptador WEKA (Aluno 8)
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'projeto_sad.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'projeto_sad.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ====================================================================
# CONFIGURAÇÕES ESPECÍFICAS DO PROJETO SAD (RDC 330)
# ====================================================================

# Configuração para Login
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/home/'

# Configuração de Arquivos de Mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ====================================================================
# AES-256 — CHAVE DE CRIPTOGRAFIA DOS ARQUIVOS
# ====================================================================

AES_KEY_BASE64 = os.getenv("AES_KEY_BASE64")
if not AES_KEY_BASE64:
    raise RuntimeError("AES_KEY_BASE64 não definida no .env")

try:
    AES_KEY = base64.b64decode(AES_KEY_BASE64)
except Exception:
    raise RuntimeError("AES_KEY_BASE64 inválida. Não foi possível decodificar Base64.")

if len(AES_KEY) != 32:
    raise RuntimeError("AES_KEY precisa ter exatamente 32 bytes (256 bits).")

# ====================================================================
# REST FRAMEWORK
# ====================================================================

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}

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

# Caminho completo para o modelo
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

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'weka_adapter': {
            'handlers': ['console'],
            'level': WEKA_LOG_LEVEL,
            'propagate': False,
        },
    },
}
