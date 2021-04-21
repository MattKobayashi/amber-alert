# amber-alert

## How to run

```Shell
docker build -t --name amber-alert .

docker run -d --name amber-alert amber-alert
```

## Environment variables

- TZ - Sets the timezone for logs (uses tzdata format, e.g. "Australia/Brisbane". Defaults to UTC)
- POSTCODE - postcode to query the Amber Electric API for prices
- WEBHOOK_URL - Sets the URL for your webhook (Discord-compatible, may work with other webhooks)
- PRICE_HIGH - Sets the upper price limit for high price alerts in c/kWh (Defaults to 20)
- PRICE_LOW - Sets the lower price limit for low price alerts in c/kWh (Defaults to 10)
- PRICE_TYPE - Select from alerts based on 5-min pricing or 30-min average pricing (Defaults to 30-min)
