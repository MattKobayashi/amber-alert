import requests
import json
import pickle
import os
from time import strftime, localtime

# Create pickle file if it doesn't already exist
if not os.path.isfile('/opt/amber/data/lastprice.pkl'):
    blankPrice = 0
    with open('data/lastprice.pkl', 'wb') as file:
        pickle.dump(blankPrice, file)
        file.close()

# Read last price from pickle file
with open('/opt/amber/data/lastprice.pkl', 'rb') as file:
    lastPrice = pickle.load(file)
    file.close()

# Print last price
print("Last price: ", lastPrice)

# Set the URL for the Amber Electric API
apiUrl = 'https://api.amberelectric.com.au/prices/listprices'

# Get current price data from the API and parse the JSON
apiResponse = requests.post(apiUrl, json={ "postcode": str(os.environ.get('POSTCODE')) })
priceData = json.loads(apiResponse.text)

# Get the fixed and variable prices into variables
fixedPrice = float(priceData['data']['staticPrices']['E1']['totalfixedKWHPrice'])
lossFactor = float(priceData['data']['staticPrices']['E1']['lossFactor'])
wholesalePrice = float(priceData['data']['variablePricesAndRenewables'][48]['wholesaleKWHPrice'])
period = str(priceData['data']['variablePricesAndRenewables'][48]['period'])

# Print the API period
print("API period: ", period)

# Calculate the current price based on the fixed and variable prices
currentPrice = fixedPrice + lossFactor * wholesalePrice
currentPrice2 = "{:.2f}".format(currentPrice)

# Print the current price
print("Current price: ", currentPrice)

# Configure the Discord webhook URL and post data
webhookUrl = str(os.environ.get('DISCORD_WH_URL'))
priceHigh = float(os.environ.get('PRICE_HIGH'))
priceLow = float(os.environ.get('PRICE_LOW'))
priceHighMsg = { "content": "Power price is above " + str(priceHigh) + "c/kWh!\n\nCurrent price is: " + currentPrice2 + "c/kWh.\n\n@everyone" }
priceLowMsg = { "content": "Power price is below " + str(priceLow) + "c/kWh!\n\nCurrent price is: " + currentPrice2 + "c/kWh.\n\n@everyone" }
priceNormalMsg = { "content": "Power prices have returned to normal.\n\nCurrent price is: " + currentPrice2 + "c/kWh.\n\n@everyone" }
priceNegMsg = { "content": "Power prices are negative!\n\nCurrent price is: " + currentPrice2 + "c/kWh.\n\n@everyone" }

# High price alert
if currentPrice > priceHigh:
    if lastPrice <= priceHigh:
        requests.post(webhookUrl, data=priceHighMsg)

# Low price alert
if currentPrice < priceLow:
    if lastPrice >= priceLow:
        requests.post(webhookUrl, data=priceLowMsg)

# Return to normal alert
if currentPrice >= priceLow and currentPrice <= priceHigh:
    if lastPrice < priceLow or lastPrice > priceHigh:
        requests.post(webhookUrl, data=priceNormalMsg)

# Negative price alert
if currentPrice < 0:
    if lastPrice >= 0:
        requests.post(webhookUrl, data=priceNegMsg)

# Write the current price to the pickle file
with open('/opt/amber/data/lastprice.pkl', 'wb') as file:
    pickle.dump(currentPrice, file)
    file.close()

# Print script completion to log
print("\nScript executed successfully at: " + strftime("%a %d %b %Y %H:%M:%S", localtime()) + "\n\n")
