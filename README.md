# amber-alert

## How to run

```Shell
docker build -t --name amber-alert .

docker run -d --name amber-alert amber-alert
```

## Environment variables

- TZ - Sets the timezone for logs (uses tzdata format, e.g. "Australia/Brisbane")
- POSTCODE - postcode to query the Amber Electric API for prices
- DISCORD_WH_URL - Sets the URL for your Discord webhook
- PRICE_HIGH - Sets the upper price limit for high price alerts in c/kWh (default is 20)
- PRICE_LOW - Sets the lower price limit for low price alerts in c/kWh (default is 10)
