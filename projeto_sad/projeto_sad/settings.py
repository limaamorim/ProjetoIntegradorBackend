"""
Django settings for projeto_sad project.
"""
from dotenv import load_dotenv
import base64
from pathlib import Path
import os # Importação necessária para MEDIA_ROOT

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis do .env
load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# (Mantenha o seu Secret Key gerado)

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

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # SEU APP: 'nucleo' (Obrigatório)
    'nucleo',
    # REMOVIDO: 'encrypted_fields' (Para evitar erro C++)
    'simulador',  #<<  app duda :)
    'rest_framework',  #<<  app duda :)

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

# Configuração Padrão de Templates (Não precisa de alteração)
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
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation (Não alteramos)
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br' # Mudado para português
TIME_ZONE = 'America/Sao_Paulo' # Fuso horário do Brasil

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ====================================================================
# CONFIGURAÇÕES ESPECÍFICAS DO PROJETO SAD (RDC 330)
# ====================================================================

# 1. Configuração para Login (RDC 330 exige login logo na entrada)
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/home/'

# 2. CONFIGURAÇÃO DE ARQUIVOS DE MÍDIA (Uploads de Imagens e PDFs)
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

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}
