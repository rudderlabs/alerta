FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

LABEL maintainer="Nick Satterly <nick.satterly@gmail.com>"

ARG BUILD_DATE=now
ARG VCS_REF
ARG VERSION
ARG COMMIT_ID_VALUE
ENV SERVER_VERSION=${VERSION}
ENV CLIENT_VERSION=8.5.0
ENV WEBUI_VERSION=8.5.0
ENV COMMIT_ID=${COMMIT_ID_VALUE}

LABEL org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.url="https://alerta.io" \
    org.label-schema.vcs-url="https://github.com/alerta/docker-alerta" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.version=$VERSION \
    org.label-schema.schema-version="1.0.0-rc.1"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    gnupg2 \
    libldap2-dev \
    libpq-dev \
    libsasl2-dev \
    postgresql-client \
    python3-dev \
    supervisor \
    xmlsec1 && \
    apt-get -y clean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://nginx.org/keys/nginx_signing.key | apt-key add - && \
    echo "deb https://nginx.org/packages/debian/ buster nginx" | tee /etc/apt/sources.list.d/nginx.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    nginx && \
    apt-get -y clean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

COPY requirements*.txt /app/
# hadolint ignore=DL3013
RUN pip install --no-cache-dir pip virtualenv && \
    python3 -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade setuptools && \
    /venv/bin/pip install --no-cache-dir --requirement /app/requirements.txt && \
    /venv/bin/pip install --no-cache-dir --requirement /app/requirements-docker.txt
ENV PATH $PATH:/venv/bin

RUN /venv/bin/pip install alerta==${CLIENT_VERSION} alerta-server==8.6.3
COPY install-plugins.sh /app/install-plugins.sh
COPY plugins.txt /app/plugins.txt
RUN /app/install-plugins.sh
ADD rudder-alerta-enrichment-plugin/ /opt/rudder-alerta-enrichment-plugin/
# RUN cd /opt/rudder-alerta-enrichment-plugin && /venv/bin/pip install -r requirements.txt && mv rudder_enrichment /venv/lib/python3.7/site-packages/ && rm -rf /opt/rudder-alerta-enrichment-plugin/
RUN cd /opt/rudder-alerta-enrichment-plugin && /venv/bin/pip install .


ENV ALERTA_SVR_CONF_FILE /app/alertad.conf
ENV ALERTA_CONF_FILE /app/alerta.conf

ADD https://github.com/alerta/alerta-webui/releases/download/v${WEBUI_VERSION}/alerta-webui.tar.gz /tmp/webui.tar.gz
RUN tar zxvf /tmp/webui.tar.gz -C /tmp && \
    mv /tmp/dist /web
COPY config.json /web/config.json

COPY wsgi.py /app/wsgi.py
COPY uwsgi.ini /app/uwsgi.ini
COPY nginx.conf /app/nginx.conf

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

RUN chgrp -R 0 /app /venv /web && \
    chmod -R g=u /app /venv /web && \
    useradd -u 1001 -g 0 -d /app alerta

USER 1001

ENV HEARTBEAT_SEVERITY major
ENV HK_EXPIRED_DELETE_HRS 2
ENV HK_INFO_DELETE_HRS 12

COPY docker-entrypoint.sh /usr/local/bin/
COPY supervisord.conf /app/supervisord.conf

ADD . /app
ARG FLASK_APP
ARG DATABASE_URL
ARG AUTH_REQUIRED
ARG ADMIN_USERS
ARG ADMIN_KEY
ARG STATS_URL
ARG STATS_PORT
ARG RUDDER_CONFIG_BACKEND_SERVICE_BASE_URL
ARG RUDDER_CONFIG_BACKEND_ADMIN_USERNAME
ARG RUDDER_CONFIG_BACKEND_ADMIN_PASSWORD
ARG RUDDER_CONFIG_BACKEND_DATA_CACHE_TTL
ARG RUDDER_CONFIG_BACKEND_CACHE_STORE_MAX_SIZE
ARG RUDDER_WEB_APP_URL_PREFIX
ARG DITTO_JSON_PATH
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 8080
CMD ["supervisord", "-c", "/app/supervisord.conf"]

# CMD ["tail","-f","/dev/null"]
