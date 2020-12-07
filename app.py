import requests
import json
import pickle
import os
from time import strftime, localtime

# Create pickle file if it doesn't already exist
if not os.path.isfile('lastprice.pkl'):
    blankPrice = 0
    with open('lastprice.pkl', 'wb') as file:
        pickle.dump(blankPrice, file)
        file.close()

# Read last price from pickle file
with open('lastprice.pkl', 'rb') as file:
    lastPrice = pickle.load(file)
    file.close()

# Print last price
print("Last price: ", lastPrice)

# Set the URL for the Amber Electric API
apiUrl = 'https://api.amberelectric.com.au/prices/listprices'

# Get current price data from the API and parse the JSON
apiResponse = requests.post(apiUrl, json={ "postcode": "4066" })
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
webhookUrl = 'https://discord.com/api/webhooks/785446655892652082/anHVQySSew6byzPblkqp1gyOwsTM8e9w4rnLSNZ4SdZxWrQ7LTBfZIUnhh9TIVkhUvVC'
priceHigh = { "content": "Power price is above 20c/kWh!\n\nCurrent price is: " + currentPrice2 + "c/kWh\n\n@everyone" }
priceLow = { "content": "Power price is below 10c/kWh!\n\nCurrent price is: " + currentPrice2 + "c/kWh\n\n@everyone" }

# High price alert
if currentPrice > 20:
    if lastPrice <= 20:
        requests.post(webhookUrl, data=priceHigh)

# Low price alert
if currentPrice < 10:
    if lastPrice >= 10:
        requests.post(webhookUrl, data=priceLow)

# Write the current price to the pickle file
with open('lastprice.pkl', 'wb') as file:
    pickle.dump(currentPrice, file)
    file.close()

# Print script completion to log
print("\nScript executed successfully at: " + strftime("%a %d %b %Y %H:%M:%S", localtime()) + "\n\n")
