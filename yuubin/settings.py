import os

from envparse import env

REDIS_PREFIX = os.getenv("REDIS_PREFIX", "yuubin:")

REDIS_MAIL_QUEUE = os.getenv("REDIS_MAIL_QUEUE", f"{REDIS_PREFIX}:mail_queue")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", 5025))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_TLS = env.bool("SMTP_TLS", default=False)

MAIL_FROM = os.getenv("MAIL_FROM", "account@example.tld")
MAIL_RETURN = os.getenv("MAIL_RETURN_PATH", "returns@example.tld")

MAIL_CONNECTOR = os.getenv("MAIL_CONNECTOR", "yuubin.connectors.smtp")

SSL_CERT = os.getenv("SSL_CERT", "./ssl-cert")
SSL_KEY = os.getenv("SSL_CERT", "./ssl-private-key")

SSL_ENABLED = env.bool("SSL_ENABLED", default=True)

AUTH_HTPASSWD_FILE = os.getenv("AUTH_HTTPASSWD_FILE", default="")
