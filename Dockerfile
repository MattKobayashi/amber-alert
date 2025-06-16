FROM python:3.13.5-alpine@sha256:9b4929a72599b6c6389ece4ecbf415fd1355129f22bb92bb137eea098f05e975
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
