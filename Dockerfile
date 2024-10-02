FROM python:3.12.7-alpine3.20

WORKDIR /opt/amber

ARG TARGETPLATFORM
ENV SUPERCRONIC_SHA1SUM_amd64=cd48d45c4b10f3f0bfdd3a57d054cd05ac96812b \
    SUPERCRONIC_SHA1SUM_arm=75e065bf0909f920b06d5bd797c0e6b31e68b112 \
    SUPERCRONIC_SHA1SUM_arm64=512f6736450c56555e01b363144c3c9d23abed4c \
    SUPERCRONIC_SHA1SUM_i386=3436985298ce241d7d9477eb9eab164b582717a8 \
    SUPERCRONIC_VERSION=v0.2.29

RUN if [ "$TARGETPLATFORM" = "linux/amd64" ]; then ARCH=amd64; elif [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then ARCH=arm; elif [ "$TARGETPLATFORM" = "linux/arm64" ]; then ARCH=arm64; elif [ "$TARGETPLATFORM" = "linux/i386" ]; then ARCH=i386; else exit 1; fi \
    && export SUPERCRONIC="supercronic-linux-${ARCH}" \
    && export SUPERCRONIC_URL="https://github.com/aptible/supercronic/releases/download/${SUPERCRONIC_VERSION}/${SUPERCRONIC}" \
    && wget "$SUPERCRONIC_URL" \
    && eval SUPERCRONIC_SHA1SUM='$SUPERCRONIC_SHA1SUM_'$ARCH \
    && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "${SUPERCRONIC}" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic \
    && addgroup -S amber && adduser -S amber -G amber \
    && mkdir -p data \
    && chown amber:amber data \
    && apk --no-cache upgrade \
    && apk add --no-cache tzdata

USER amber

COPY amber-cron ./crontab/amber-cron
COPY app.py app.py
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV TZ=UTC \
    AMBER_API_KEY= \
    AMBER_SITE_ID= \
    WEBHOOK_URL= \
    ALERT_HIGH=25 \
    ALERT_LOW=10 \
    DATA_RES=30

VOLUME ["/opt/amber/data"]

ENTRYPOINT ["supercronic", "./crontab/amber-cron"]

LABEL org.opencontainers.image.authors="MattKobayashi <matthew@kobayashi.au>"
