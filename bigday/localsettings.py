# email server configuration
EMAIL_HOST = 'yourHost'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'yourUser'
EMAIL_HOST_PASSWORD = 'YourSecret'
EMAIL_PORT = 587

# your standard sending addresses
DEFAULT_WEDDING_EMAIL = 'john_johnk@hotmail.com'
DEFAULT_WEDDING_REPLY_EMAIL = 'julietteah@hotmail.fr'
# put email addresses here if you want to cc someone on all your invitations
WEDDING_CC_LIST = []

# your names
BRIDE_AND_GROOM = 'J&J '
# the location of your wedding
WEDDING_LOCATION = 'Paris'
# the date of your wedding
WEDDING_DATE = '9-11 Janvier 2026'
# this is used in links in save the date / invitations
WEDDING_WEBSITE_URL = 'https://wedding.johnjohnk.duckdns.org'

# Django secret. You must change this!
SECRET_KEY = 'Decibel-Dutiful-Nintendo-Gala0'


ALLOWED_HOSTS = [
    "wedding.johnjohnk.duckdns.org",
    "192.168.1.39",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://wedding.johnjohnk.duckdns.org",
    "https://192.168.1.39",
    "https://localhost",
    "https://127.0.0.1",
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
USE_X_FORWARDED_HOST = True

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static_root"