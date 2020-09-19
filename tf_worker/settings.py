import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'home',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "most",
        'USER': "root",
        'PASSWORD': "Nghia.123",
        'HOST': "127.0.0.1",
        'PORT': "3306",
    }
}

RABBITMQ_USER = "guest"
RABBITMQ_PWD = "guest"
RABBITMQ_HOST = "127.0.0.1"
RABBITMQ_PORT = "5672"

# SECURITY WARNING: Modify this secret key if using in production!
SECRET_KEY = 'mqht8av5fo4c+si33ipd28^i&65-&)1=1+3-upqvqru=$4sh)z'
# ------------------------------- End Django ORM settings -------------------------------
