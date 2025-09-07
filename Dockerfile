FROM alpine:3.22.1@sha256:4bcff63911fcb4448bd4fdacec207030997caf25e9bea4045fa6c8c44de311d1

# renovate: datasource=repology depName=alpine_3_22/supercronic
ENV SUPERCRONIC_VERSION="0.2.33-r7"
# renovate: datasource=repology depName=alpine_3_22/tzdata versioning=loose
ENV TZDATA_VERSION="2025b-r0"
# renovate: datasource=repology depName=alpine_3_22/uv
ENV UV_VERSION="0.7.22-r0"

RUN apk --no-cache add \
    supercronic="${SUPERCRONIC_VERSION}" \
    tzdata="${TZDATA_VERSION}" \
    uv="${UV_VERSION}"

WORKDIR /opt/amber
RUN addgroup -S amber && adduser -S amber -G amber \
    && mkdir -p data \
    && chown amber:amber data
USER amber
COPY amber-cron ./crontab/amber-cron
COPY main.py pyproject.toml /opt/amber/
ENV TZ=UTC \
    AMBER_SITE_ID= \
    WEBHOOK_URL= \
    ALERT_HIGH=25 \
    ALERT_LOW=10 \
    DATA_RES=30
VOLUME ["/opt/amber/data"]
ENTRYPOINT ["/usr/bin/supercronic", "./crontab/amber-cron"]
LABEL org.opencontainers.image.authors="MattKobayashi <matthew@kobayashi.au>"
