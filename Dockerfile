FROM python:3.13.3-alpine3.21@sha256:f50e1ca5ac620527f8a8acc336cab074dc8a418231380cd6d9eafb4103931f91
WORKDIR /opt/amber
RUN apk --no-cache add supercronic \
    && addgroup -S amber && adduser -S amber -G amber \
    && mkdir -p data \
    && chown amber:amber data \
    && apk --no-cache add tzdata uv
USER amber
COPY amber-cron ./crontab/amber-cron
COPY main.py main.py
ENV TZ=UTC \
    AMBER_SITE_ID= \
    WEBHOOK_URL= \
    ALERT_HIGH=25 \
    ALERT_LOW=10 \
    DATA_RES=30
VOLUME ["/opt/amber/data"]
ENTRYPOINT ["/usr/bin/supercronic", "./crontab/amber-cron"]
LABEL org.opencontainers.image.authors="MattKobayashi <matthew@kobayashi.au>"
