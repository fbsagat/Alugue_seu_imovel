from pathlib import Path
from django.contrib.messages import constants as messages
import os, environ, dj_database_url
from Alugue_seu_imovel import settings

# CONFIGURAÇÕES CUSTOMIZADAS DO SITE \/ -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

SITE_NAME = 'Alugue Seu imóvel'
SITE_URL = 'https://alugueseuimovel.up.railway.app'
USAR_DB = 2
# /\ 1. SQlite3 Local | 2. PostGreSQL + railway | 3. PostGreSQL + Render.com

# tempo para apagar a form inválida da navbar das sessions
TEMPO_SESSION_FORM = 60

# Configurações do gerador de dados fictícios (home.views / home.fakes_test):
# Total a ser criado para cada item \/
contrato = 4
FICT_QTD = {'locatario': 5, 'imovel_g': 2, 'imovel': 5, 'contrato': contrato, 'pagamento': contrato * 2, 'gasto': 3,
            'nota': 3, 'user': 5}

# Tamanho em ‘megabytes’ permitido para envio de imagens para o site, padrão para todos os campos \/
TAMANHO_DAS_IMAGENS_Mb = 4

# CONFIGURAÇÕES CUSTOMIZADAS DO SITE /\ -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))

env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: keep the secret key used in production secret!
TOKEN_CSRF = os.getenv('TOKEN_CSRF')
CSRF_TRUSTED_ORIGINS = ''
if TOKEN_CSRF:
    SECRET_KEY = TOKEN_CSRF
    CSRF_TRUSTED_ORIGINS = [SITE_URL, ]
else:
    SECRET_KEY = 'django-insecure-)t-u^e^z1+z&ni%#(gd2vuc^0uxovq(5k4(w_=r3-2jr^*snqj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [SITE_URL.split('//')[1], 'localhost', '127.0.0.1']

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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
        'DIRS': [BASE_DIR, 'templates/',
                 ],
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
if USAR_DB == 1:
    # SQlite3 Local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_admlco32_.sqlite3',
        }
    }
elif USAR_DB == 2:
    # PostGreSQL + railway.app ( with dj-database-url)
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        DATABASES = {'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=1800)}
    else:
        # Para criar a base de dados inicial(makemigrations e migrate). Conecta e cria.
        DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql',
                                 'NAME': 'railway',
                                 'USER': 'postgres',
                                 'PASSWORD': 'HknBUcYGjg3ySf13lXNn',
                                 'HOST': 'containers-us-west-40.railway.app',
                                 'PORT': '6017',
                                 }
                     }
elif USAR_DB == 3:
    # PostGreSQL + Render.com ( with dj-database-url)
    DATABASES = {
        'default': dj_database_url.parse(env('DATABASE_URL'))
    }

# Password validation
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

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
if USAR_DB == 3:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/').replace('\\', '/')
MEDIA_URL = '/media/'

# Default primary key field type
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
