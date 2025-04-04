# amber-alert

A webhook-based price alerter for Amber Electric, an Australian electricity retailer that passes through live wholesale pricing directly to customers.

## How to run

For secrets support, it is required to use [Docker Compose](https://docs.docker.com/compose/). An example Compose script can be found in this repo (docker-compose.yaml). Edit the file to suit your needs, then run the following:

```Shell
docker compose up --detach
```

## Environment variables

- TZ - Sets the timezone for logs (in `tzdata` format, e.g. "Australia/Brisbane". Defaults to UTC)
- AMBER_SITE_ID: The site ID for the site you want to get price alerts for. This can be found by querying the Amber API's /sites endpoint, documentation can be found in the [Amber developer portal](https://app.amber.com.au/developers).
- WEBHOOK_URL: Sets the URL for your webhook (Discord-compatible, may work with other webhook services).
- ALERT_HIGH: Sets the upper price limit for high price alerts in c/kWh (Defaults to 25).
- ALERT_LOW - Sets the lower price limit for low price alerts in c/kWh (Defaults to 10).

## Docker secrets

- AMBER_API_KEY: Your unique Amber API key. Generate one in the [Amber developer portal](https://app.amber.com.au/developers).
