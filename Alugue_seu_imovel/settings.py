from pathlib import Path
from django.contrib.messages import constants as messages
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)t-u^e^z1+z&ni%#(gd2vuc^0uxovq(5k4(w_=r3-2jr^*snqj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

X_FRAME_OPTIONS = 'SAMEORIGIN'

INTERNAL_IPS = [
    "127.0.0.1",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'django_cleanup.apps.CleanupConfig',

    'home',

    'crispy_forms',
    'crispy_bootstrap5',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

]

ROOT_URLCONF = 'Alugue_seu_imovel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.new_context.titulo_pag',
                'home.new_context.forms_da_navbar',
            ],
        },
    },
]

WSGI_APPLICATION = 'Alugue_seu_imovel.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_admlco32_.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "home.Usuario"

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/').replace('\\', '/')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'home:Login'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Configurações do cryspy-forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Substituição do nome das tags do django para as compatíveis com o bootstrap
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Configurações da biblioteca de redimendionamento das imagens enviadas pelos usuários:
DJANGORESIZED_DEFAULT_SIZE = [1080, None]
DJANGORESIZED_DEFAULT_SCALE = 0.5
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

# Configurações da biblioteca de notificações (django-notifications-hq):
DJANGO_NOTIFICATIONS_CONFIG = {'SOFT_DELETE': True}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# A PARTIR DAQUI CONFIGURAÇÕES CUSTOMIZADAS DO SITE \/

SITE_LINK = 'www.alugueseuimovel.com.br'
SITE_NAME = 'Alugue Seu imóvel'

# tempo para apagar a form inválida da navbar das sessions
TEMPO_SESSION_FORM = 60

# Configurações do gerador de dados fictícios (home.views / home.fakes_test):
# Total a ser criado para cada item \/
contrato = 4
FICT_QTD = {'locatario': 5, 'imovel_g': 2, 'imovel': 5, 'contrato': contrato, 'pagamento': contrato * 2, 'gasto': 3,
            'nota': 3, 'user': 5}

# Tamanho em ‘megabytes’ permitido para envio de imagens para o site, padrão para todos os campos \/
TAMANHO_DAS_IMAGENS_Mb = 4
