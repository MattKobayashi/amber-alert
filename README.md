# amber-alert
A webhook-based price alerter for Amber, an Australian electricity retailer that passes through live wholesale pricing directly to customers.

## How to run

```Shell
docker build -t --name amber-alert .

docker run -d --name amber-alert amber-alert
```

## Environment variables

- TZ - Sets the timezone for logs (in `tzdata` format, e.g. "Australia/Brisbane". Defaults to UTC)
- AMBER_API_KEY: Your unique Amber API key. Generate one in the [Amber portal](https://app.amber.com.au/developers).
- AMBER_SITE_ID: 
- WEBHOOK_URL: Sets the URL for your webhook (Discord-compatible, may work with other webhooks).
- ALERT_HIGH: Sets the upper price limit for high price alerts in c/kWh (Defaults to 25).
- ALERT_LOW - Sets the lower price limit for low price alerts in c/kWh (Defaults to 10).
