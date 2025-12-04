import os
from pathlib import Path  # IMPORTANTE: Usamos Path para rutas modernas
import dj_database_url

# 1. CORRECCIÓN: Usamos Path en lugar de os.path para que funcione el operador '/'
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SEGURIDAD: Intentamos leer la SECRET_KEY de las variables de entorno de Render.
# Si no existe (en local), usa la clave por defecto (insegura, solo para dev).
SECRET_KEY = os.environ.get('SECRET_KEY', default='-_&+lsebec(whhw!%n@ww&1j=4-^j_if9x8$q778+99oz&!ms2')

# DEBUG será False si estamos en Render (seguridad), True en local.
DEBUG = 'RENDER' not in os.environ

# 3. CORRECCIÓN: Añadimos el host que Render nos asigna automáticamente.
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# También permitimos localhost para pruebas locales
ALLOWED_HOSTS.extend(["localhost", "127.0.0.1", ])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'control_escolar_desit_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # WhiteNoise justo después de Security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'control_escolar_desit_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'control_escolar_desit_api.wsgi.application'


# ====================================================================
# CORRECCIÓN FINAL DE BASE DE DATOS PARA EVITAR UnknownSchemeError
# ====================================================================

DATABASES = {
    'default': dj_database_url.config(
        # 1. Obtiene DATABASE_URL de Render. Si no existe, usa la cadena 'not_found'
        #    (Esto evita que una cadena vacía "" rompa dj-database-url)
        default=os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600
    )
}

# ====================================================================
# FIN DEL BLOQUE DE BASE DE DATOS
# ====================================================================


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS Y MEDIA ---

STATIC_URL = '/static/'
# Ahora sí funciona el operador '/' porque BASE_DIR es un objeto Path
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 4. CORRECCIÓN: Configuración necesaria para que WhiteNoise comprima y sirva archivos
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- CORS ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "https://control-escolar-webapp.onrender.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'control_escolar_desit_api.models.BearerTokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}