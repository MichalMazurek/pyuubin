import dotenv
from pydantic import BaseSettings, SecretStr

dotenv.load_dotenv()


class Settings(BaseSettings):

    redis_prefix: str = "pyuubin:"
    redis_mail_queue: str = "pyuubin::mail_queue"
    redis_url: str = "redis://localhost:6379"

    smtp_host: str = "localhost"
    smtp_port: int = 5025
    smtp_user: str = ""
    smtp_password: SecretStr = ""
    smtp_tls: bool = False

    mail_from: str = "account@example.ltd"
    mail_return: str = "returns@exampple.tld"
    mail_connector: str = "pyuubin.connectors.smtp"

    auth_htpasswd_file: str = ""

    class Config:
        env_prefix = "PYUUBIN_"


settings = Settings()


def print_env_variables():

    for key, value in settings.dict().items():
        print(f"{settings.Config.env_prefix}{key.upper()}={value}")
