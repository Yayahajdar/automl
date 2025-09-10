from .settings import *

# Utiliser SQLite pour les tests afin d'éviter les privilèges PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # Fichier de test persistant; remplacez par ":memory:" si vous préférez en mémoire
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

# Accélère un peu les tests utilisateur si présents
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Evite toute sortie mail réelle pendant les tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Hôtes utilisés par le client de test Django/DRF
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]