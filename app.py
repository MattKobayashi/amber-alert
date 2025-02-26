# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests==2.32.3",
# ]
# ///

#!/usr/bin/env python3
import json
import os
from datetime import datetime
import requests

# Create price data JSON file if it doesn't already exist
if not os.path.isfile("data/priceData.json"):
    blankPrice = {"lastPrice": 0}
    with open("data/priceData.json", "w", encoding="utf-8") as file:
        json.dump(blankPrice, file)

# Read price data from JSON file
with open("data/priceData.json", "r", encoding="utf-8") as file:
    priceDataFile = json.load(file)

# Get the current datetime
now = datetime.now()

# Load environment variables
try:
    with open("/run/secrets/AMBER_API_KEY", "r", encoding="utf-8") as apiKey_secret:
        apiKey = apiKey_secret.read().strip()
except FileNotFoundError as e:
    raise Exception("API key secret not defined.") from e
except Exception as e:
    raise Exception(f"Error reading API key secret: {e}") from e

try:
    siteId = os.environ["AMBER_SITE_ID"]
    webhookUrl = os.environ["WEBHOOK_URL"]
    alertHigh = float(os.environ["ALERT_HIGH"])
    alertLow = float(os.environ["ALERT_LOW"])
    priceRes = os.environ["DATA_RES"]
except KeyError as e:
    raise Exception(f"Missing environment variable: {e}") from e
except ValueError as e:
    raise Exception(f"Invalid value for environment variable: {e}") from e

# Set the URL for the Amber Electric API
apiUrl = (
    f"https://api.amber.com.au/v1/sites/{siteId}/prices/current?resolution={priceRes}"
)

# Get current price data from the API and parse the JSON
try:
    apiResponse = requests.get(
        apiUrl,
        headers={"accept": "application/json", "Authorization": f"Bearer {apiKey}"}
    )
    apiResponse.raise_for_status()
    priceDataApi = apiResponse.json()
except requests.exceptions.RequestException as e:
    raise Exception(f"API request failed: {e}") from e

# Set variables
currentPrice = float(priceDataApi[0]["perKwh"])
currentPrice2 = "{:.2f}".format(currentPrice)
lastPrice = float(priceDataFile["lastPrice"])

# Print last price
print("Last price:", lastPrice)
print("Current price:", currentPrice)

# Alert message strings
alertHighMsg = {
    "content": "Power price is above "
    + str(alertHigh)
    + "c/kWh!\n\nCurrent price is: "
    + str(currentPrice2)
    + "c/kWh.\n\n@everyone"
}
alertLowMsg = {
    "content": "Power price is below "
    + str(alertLow)
    + "c/kWh!\n\nCurrent price is: "
    + str(currentPrice2)
    + "c/kWh.\n\n@everyone"
}
alertNormalMsg = {
    "content": "Power prices have returned to normal.\n\nCurrent price is: "
    + str(currentPrice2)
    + "c/kWh.\n\n@everyone"
}
alertNegMsg = {
    "content": "Power prices are negative!\n\nCurrent price is: "
    + str(currentPrice2)
    + "c/kWh.\n\n@everyone"
}

# High price alert
if currentPrice > alertHigh and lastPrice <= alertHigh:
    requests.post(webhookUrl, data=alertHighMsg)

# Low price alert
if currentPrice < alertLow and currentPrice >= 0 and lastPrice >= alertLow:
    requests.post(webhookUrl, data=alertLowMsg)

# Return to normal alert
if (
    currentPrice >= alertLow
    and currentPrice <= alertHigh
    and (lastPrice < alertLow or lastPrice > alertHigh)
):
    requests.post(webhookUrl, data=alertNormalMsg)

# Negative price alert
if currentPrice < 0 and lastPrice >= 0:
    requests.post(webhookUrl, data=alertNegMsg)

# Update the last prices to match the current ones
priceDataFile["lastPrice"] = currentPrice

# Write updated price data to the JSON file
with open("data/priceData.json", "w", encoding="utf-8") as file:
    json.dump(priceDataFile, file)
    file.close()

# Print script completion to log
print(
    "\nScript executed successfully at: "
    + datetime.strftime(now, "%A %d %b %Y %H:%M:%S")
    + "\n\n"
)
