FROM python:3.7

ARG version
ARG repository

RUN apt-get update
RUN apt-get install -y libssl-dev swig

ENV REDIS_URL=redis://redis
ENV REDIS_PREFIX=yuubin:
ENV HTTP_HOST=0.0.0.0
ENV HTTP_PORT=8080
ENV DEBUG=0
ENV SSL_ENABLED=yes
ENV SSL_CERT=/cert.pem
ENV SSL_KEY=/cert.pkey
ENV AUTH_HTPASSWD_FILE=""

ENV YUUBIN_VERSION=$version

ADD ./install.sh /install.sh

RUN bash install.sh $repository
RUN rm /install.sh

WORKDIR  /srv

CMD [ "python3", "-m", "yuubin" ]

