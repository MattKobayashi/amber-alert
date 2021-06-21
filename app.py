import requests
import json
import os
from datetime import datetime

# Create price data JSON file if it doesn't already exist
if not os.path.isfile("data/priceData.json"):
    blankPrice = {"lastPrice": 0}
    with open("data/priceData.json", "w") as file:
        json.dump(blankPrice, file)
        file.close()

# Read price data from JSON file
with open("data/priceData.json", "r") as file:
    priceDataFile = json.load(file)
    file.close()

# Get the current datetime
now = datetime.now()

# Load environment variables
apiKey = os.environ.get("AMBER_API_KEY")
siteId = os.environ.get("AMBER_SITE_ID")
webhookUrl = os.environ.get("WEBHOOK_URL")
alertHigh = float(os.environ.get("ALERT_HIGH"))
alertLow = float(os.environ.get("ALERT_LOW"))
priceRes = os.environ.get("DATA_RES")

# Set the URL for the Amber Electric API
apiUrl = (
    f"https://api.amber.com.au/v1/sites/{siteId}/prices/current?resolution={priceRes}"
)

# Get current price data from the API and parse the JSON
apiResponse = requests.get(
    apiUrl, headers={"accept": "application/json", "Authorization": f"Bearer {apiKey}"}
)
priceDataApi = json.loads(apiResponse.text)

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
with open("data/priceData.json", "w") as file:
    json.dump(priceDataFile, file)
    file.close()

# Print script completion to log
print(
    "\nScript executed successfully at: "
    + datetime.strftime(now, "%A %d %b %Y %H:%M:%S")
    + "\n\n"
)
