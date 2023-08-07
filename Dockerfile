FROM python:3-alpine

WORKDIR /opt/amber

ARG TARGETPLATFORM
ENV SUPERCRONIC_SHA1SUM_amd64=7a79496cf8ad899b99a719355d4db27422396735 \
    SUPERCRONIC_SHA1SUM_arm=d8124540ebd8f19cc0d8a286ed47ac132e8d151d \
    SUPERCRONIC_SHA1SUM_arm64=e4801adb518ffedfd930ab3a82db042cb78a0a41 \
    SUPERCRONIC_SHA1SUM_i386=bcc522ec4ead6de0d564670f6499a88e35082d1f \
    SUPERCRONIC_VERSION=v0.2.26

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
