SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'classifier',

    'tests',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
