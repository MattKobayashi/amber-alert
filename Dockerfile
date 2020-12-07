FROM python:3.9-alpine3.12

WORKDIR /opt/amber

COPY amber-cron /etc/cron.d/amber-cron
COPY app.py app.py

RUN chmod 0644 /etc/cron.d/amber-cron \
    && crontab /etc/cron.d/amber-cron \
    && touch /var/log/cron.log \
    && pip install requests \
    && apk add --no-cache tzdata

ENV TZ=Australia/Brisbane
ENV POSTCODE=
ENV DISCORD_WH_URL=
ENV PRICE_HIGH=20
ENV PRICE_LOW=10

ENTRYPOINT ["crond", "-f"]
