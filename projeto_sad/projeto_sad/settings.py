import base64
from pathlib import Path
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================
# SEGURANÇA
# =============================================================

# Coloque isto no seu .env:
# SECRET_KEY="sua_chave_nova_gerada"
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não definida no .env")

DEBUG = True
ALLOWED_HOSTS = []


# =============================================================
# INSTALLED_APPS
# =============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'nucleo',
    'simulador',
]


# =============================================================
# MIDDLEWARE
# =============================================================

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


# =============================================================
# TEMPLATES (padrão)
# =============================================================

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


# =============================================================
# DATABASE
# =============================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =============================================================
# AUTH VALIDATION
# =============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================
# INTERNACIONALIZAÇÃO
# =============================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# =============================================================
# STATIC / MEDIA
# =============================================================

STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================
# AES-256 — CHAVE DE CRIPTOGRAFIA DOS ARQUIVOS
# =============================================================

AES_KEY_BASE64 = os.getenv("AES_KEY_BASE64")

if not AES_KEY_BASE64:
    raise RuntimeError("AES_KEY_BASE64 não definida no .env")

try:
    AES_KEY = base64.b64decode(AES_KEY_BASE64)
except Exception:
    raise RuntimeError("AES_KEY_BASE64 inválida. Não foi possível decodificar Base64.")

if len(AES_KEY) != 32:
    raise RuntimeError("AES_KEY precisa ter exatamente 32 bytes (256 bits).")


# =============================================================
# DRF
# =============================================================

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}
