import requests
import json
import os
from datetime import datetime
from statistics import mean

# Create price data JSON file if it doesn't already exist
if not os.path.isfile("data/priceData.json"):
    blankPrice = {"lastPrices":{"5min":0,"30min":0,},"currentPrices":{"5min":0,"30min":0,},"priceHistory":{"00":0,"05":0,"10":0,"15":0,"20":0,"25":0,},}
    with open("data/priceData.json", "w") as file:
        json.dump(blankPrice, file)
        file.close()

# Read price data from JSON file
with open("data/priceData.json", "r") as file:
    priceDataFile = json.load(file)
    file.close()

# Get the current datetime
now = datetime.now()

# Print last prices
print("Last 5-min price:", priceDataFile['lastPrices']['5min'])
print("Last 30-min price:", priceDataFile['lastPrices']['30min'])

# Set the URL for the Amber Electric API
apiURL = 'https://api.amberelectric.com.au/prices/listprices'

# Get current price data from the API and parse the JSON
apiResponse = requests.post(apiURL, json={ "postcode": str(os.environ.get('POSTCODE')) })
priceDataAPI = json.loads(apiResponse.text)

# Get the fixed and variable prices into variables
fixedPrice = float(priceDataAPI['data']['staticPrices']['E1']['totalfixedKWHPrice'])
lossFactor = float(priceDataAPI['data']['staticPrices']['E1']['lossFactor'])
wholesalePrice = float(priceDataAPI['data']['variablePricesAndRenewables'][48]['wholesaleKWHPrice'])
period = str(priceDataAPI['data']['variablePricesAndRenewables'][48]['period'])

# Calculate the current 5-min price based on the fixed and variable prices
priceDataFile['currentPrices']['5min'] = fixedPrice + lossFactor * wholesalePrice

# Round currentPrice to 2 sig. digits
currentPrice5Rnd = "{:.2f}".format(priceDataFile['currentPrices']['5min'])

# Print the API period
print("API period:", period)

# Print the current price
print("Current 5-min price:", priceDataFile['currentPrices']['5min'])

# Populate 30-min price list
if (now.minute >= 0 and now.minute < 5) or (now.minute >= 30 and now.minute < 35):
    priceDataFile['priceHistory']['00'] = 0
    priceDataFile['priceHistory']['05'] = 0
    priceDataFile['priceHistory']['10'] = 0
    priceDataFile['priceHistory']['15'] = 0
    priceDataFile['priceHistory']['20'] = 0
    priceDataFile['priceHistory']['25'] = 0
    priceDataFile['priceHistory']['00'] = priceDataFile['currentPrices']['5min']

if (now.minute >= 5 and now.minute < 10) or (now.minute >= 35 and now.minute < 40):
    priceDataFile['priceHistory']['05'] = priceDataFile['currentPrices']['5min']

if (now.minute >= 10 and now.minute < 15) or (now.minute >= 40 and now.minute < 45):
    priceDataFile['priceHistory']['10'] = priceDataFile['currentPrices']['5min']

if (now.minute >= 15 and now.minute < 20) or (now.minute >= 45 and now.minute < 50):
    priceDataFile['priceHistory']['15'] = priceDataFile['currentPrices']['5min']

if (now.minute >= 20 and now.minute < 25) or (now.minute >= 50 and now.minute < 55):
    priceDataFile['priceHistory']['20'] = priceDataFile['currentPrices']['5min']

if (now.minute >= 25 and now.minute < 30) or (now.minute >= 55 and now.minute < 59):
    priceDataFile['priceHistory']['25'] = priceDataFile['currentPrices']['5min']

# Print the 30-min price list
print("Current 30-min price list:", priceDataFile['priceHistory'])

# Extract values from 30-min price history
priceHistoryRaw = list(map(float, priceDataFile['priceHistory'].values()))

# Extract non-zero values from raw price history
pricesMeanList = []
for val in priceHistoryRaw:
    if val != 0:
        pricesMeanList.append(val)

# Calculate the current mean 30-min price
try:
    priceDataFile['currentPrices']['30min'] = mean(pricesMeanList)
except:
    print("Can't calculate a mean 30-min price, is this the first time the script has run?")
    priceDataFile['currentPrices']['30min'] = 0

# Print the current mean 30-min price
print("Current average 30-min price:", priceDataFile['currentPrices']['30min'])

# Round currentPrice30 to 2 sig. digits
currentPrice30Rnd = "{:.2f}".format(priceDataFile['currentPrices']['30min'])

# Define the 5-min alerts function
def alerts5Min():
    # Configure the webhook URL and post data
    webhookURL = str(os.environ.get('WEBHOOK_URL'))
    priceHigh = float(os.environ.get('PRICE_HIGH'))
    priceLow = float(os.environ.get('PRICE_LOW'))
    priceHighMsg = { "content": "Power price is above " + str(priceHigh) + "c/kWh!\n\nCurrent price is: " + currentPrice5Rnd + "c/kWh.\n\n@everyone" }
    priceLowMsg = { "content": "Power price is below " + str(priceLow) + "c/kWh!\n\nCurrent price is: " + currentPrice5Rnd + "c/kWh.\n\n@everyone" }
    priceNormalMsg = { "content": "Power prices have returned to normal.\n\nCurrent price is: " + currentPrice5Rnd + "c/kWh.\n\n@everyone" }
    priceNegMsg = { "content": "Power prices are negative!\n\nCurrent price is: " + currentPrice5Rnd + "c/kWh.\n\n@everyone" }

    # High price alert
    if priceDataFile['currentPrices']['5min'] > priceHigh and priceDataFile['lastPrices']['5min'] <= priceHigh:
        requests.post(webhookURL, data=priceHighMsg)

    # Low price alert
    if priceDataFile['currentPrices']['5min'] < priceLow and priceDataFile['currentPrices']['5min'] >= 0 and priceDataFile['lastPrices']['5min'] >= priceLow:
        requests.post(webhookURL, data=priceLowMsg)

    # Return to normal alert
    if priceDataFile['currentPrices']['5min'] >= priceLow and priceDataFile['currentPrices']['5min'] <= priceHigh and (priceDataFile['lastPrices']['5min'] < priceLow or priceDataFile['lastPrices']['5min'] > priceHigh):
        requests.post(webhookURL, data=priceNormalMsg)

    # Negative price alert
    if priceDataFile['currentPrices']['5min'] < 0 and priceDataFile['lastPrices']['5min'] >= 0:
        requests.post(webhookURL, data=priceNegMsg)

# Define the 30-min alerts function
def alerts30Min():
    # Configure the webhook URL and post data
    webhookURL = str(os.environ.get('WEBHOOK_URL'))
    priceHigh = float(os.environ.get('PRICE_HIGH'))
    priceLow = float(os.environ.get('PRICE_LOW'))
    priceHighMsg = { "content": "Power price is above " + str(priceHigh) + "c/kWh!\n\nCurrent price is: " + currentPrice30Rnd + "c/kWh.\n\n@everyone" }
    priceLowMsg = { "content": "Power price is below " + str(priceLow) + "c/kWh!\n\nCurrent price is: " + currentPrice30Rnd + "c/kWh.\n\n@everyone" }
    priceNormalMsg = { "content": "Power prices have returned to normal.\n\nCurrent price is: " + currentPrice30Rnd + "c/kWh.\n\n@everyone" }
    priceNegMsg = { "content": "Power prices are negative!\n\nCurrent price is: " + currentPrice30Rnd + "c/kWh.\n\n@everyone" }

    # High price alert
    if priceDataFile['currentPrices']['30min'] > priceHigh and priceDataFile['lastPrices']['30min'] <= priceHigh:
        requests.post(webhookURL, data=priceHighMsg)

    # Low price alert
    if priceDataFile['currentPrices']['30min'] < priceLow and priceDataFile['currentPrices']['30min'] >= 0 and priceDataFile['lastPrices']['30min'] >= priceLow:
        requests.post(webhookURL, data=priceLowMsg)

    # Return to normal alert
    if priceDataFile['currentPrices']['30min'] >= priceLow and priceDataFile['currentPrices']['30min'] <= priceHigh and (priceDataFile['lastPrices']['30min'] < priceLow or priceDataFile['lastPrices']['30min'] > priceHigh):
        requests.post(webhookURL, data=priceNormalMsg)

    # Negative price alert
    if priceDataFile['currentPrices']['30min'] < 0 and priceDataFile['lastPrices']['30min'] >= 0:
        requests.post(webhookURL, data=priceNegMsg)

# Call the relevant function for 5-min or 30-min price alerts
if os.environ.get('PRICE_TYPE') == "5":
    alerts5Min()
elif os.environ.get('PRICE_TYPE') == "30":
    alerts30Min()
else:
    exit("An incorrect price type has been entered. Please check the value for PRICE_TYPE environment variable and try again.")

# Update the last prices to match the current ones
priceDataFile['lastPrices']['5min'] = priceDataFile['currentPrices']['5min']
priceDataFile['lastPrices']['30min'] = priceDataFile['currentPrices']['30min']

# Write updated price data to the JSON file
with open('data/priceData.json', 'w') as file:
    json.dump(priceDataFile, file)
    file.close()

# Print script completion to log
print("\nScript executed successfully at: " + datetime.strftime(now, "%A %d %b %Y %H:%M:%S") + "\n\n")
