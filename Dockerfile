FROM python:3.7

RUN apt-get update
RUN apt-get install -y build-essential libssl-dev swig

ENV REDIS_URL=redis://redis
ENV REDIS_PREFIX=yuubin:
ENV HTTP_HOST=0.0.0.0
ENV HTTP_PORT=8080
ENV DEBUG=0
ENV SSL_ENABLED=yes
ENV SSL_CERT=/cert.pem
ENV SSL_KEY=/cert.pkey
ENV AUTH_HTPASSWD_FILE=""

RUN pip install .


CMD [ "python", "-m", "yuubin" ]