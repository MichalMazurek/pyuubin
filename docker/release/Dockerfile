FROM python:3.7

ARG version

ENV PYUUBIN_REDIS_MAIL_QUEUE=pyuubin::mail_queue
ENV PYUUBIN_REDIS_URL=redis://redis:6379
ENV PYUUBIN_REDIS_PREFIX=pyuubin:
ENV PYUUBIN_SMTP_HOST=smtp.gmail.com
ENV PYUUBIN_SMTP_PORT=465
ENV PYUUBIN_SMTP_USER=test@gmail.com
ENV PYUUBIN_SMTP_PASSWORD=secret
ENV PYUUBIN_SMTP_TLS=True
ENV PYUUBIN_MAIL_FROM=test@gmail.com
ENV PYUUBIN_MAIL_RETURN=test@gmail.com
ENV PYUUBIN_MAIL_CONNECTOR=pyuubin.connectors.smtp
ENV PYUUBIN_AUTH_HTPASSWD_FILE=


RUN pip install pyuubin==${version}

WORKDIR  /srv

CMD [ "hypercorn", "pyuubin.api.app:app", "--bind", "0.0.0.0:8000", "--access-log", "-", "--error-log", "-" ]

