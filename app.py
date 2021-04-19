import requests
import json
import pickle
import os
from datetime import datetime
from statistics import mean

# Create 5-min price pickle file if it doesn't already exist
if not os.path.isfile('data/lastprice5.pkl'):
    blankPrice = 0
    with open('data/lastprice5.pkl', 'wb') as file:
        pickle.dump(blankPrice, file)
        file.close()

# Create 30-min price pickle file if it doesn't already exist
if not os.path.isfile('data/lastprice30.pkl'):
    with open('data/lastprice30.pkl', 'wb') as file:
        pickle.dump(blankPrice, file)
        file.close()

# Create 30-min price list pickle file if it doesn't already exist
if not os.path.isfile('data/pricelist30.pkl'):
    blankPriceList = [None, None, None, None, None, None]
    with open('data/pricelist30.pkl', 'wb') as file:
        pickle.dump(blankPriceList, file)
        file.close()

# Read last 5-min price from pickle file
with open('data/lastprice5.pkl', 'rb') as file:
    lastPrice5 = pickle.load(file)
    file.close()

# Read last 30-min price from pickle file
with open('data/lastprice30.pkl', 'rb') as file:
    lastPrice30 = pickle.load(file)
    file.close()

# Read last 30-min price list from pickle file
with open('data/pricelist30.pkl', 'rb') as file:
    prices5Min = pickle.load(file)
    file.close()

# Get the current datetime
now = datetime.now()

# Print last prices
print("Last 5-min price:", lastPrice5)
print("Last 30-min price:", lastPrice30)

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

# Calculate the current 5-min price based on the fixed and variable prices
currentPrice5 = fixedPrice + lossFactor * wholesalePrice

# Round currentPrice to 2 sig. digits
currentPrice5Rnd = "{:.2f}".format(currentPrice5)

# Print the API period
print("API period:", period)

# Print the current price
print("Current 5-min price:", currentPrice5)

# Populate 30-min price list
if (now.minute >= 0 and now.minute < 5) or (now.minute >= 30 and now.minute < 35):
    prices5Min = [None, None, None, None, None, None]
    prices5Min[0] = currentPrice5

if (now.minute >= 5 and now.minute < 10) or (now.minute >= 35 and now.minute < 40):
    prices5Min[1] = currentPrice5

if (now.minute >= 10 and now.minute < 15) or (now.minute >= 40 and now.minute < 45):
    prices5Min[2] = currentPrice5

if (now.minute >= 15 and now.minute < 20) or (now.minute >= 45 and now.minute < 50):
    prices5Min[3] = currentPrice5

if (now.minute >= 20 and now.minute < 25) or (now.minute >= 50 and now.minute < 55):
    prices5Min[4] = currentPrice5

if (now.minute >= 25 and now.minute < 30) or (now.minute >= 55 and now.minute < 59):
    prices5Min[5] = currentPrice5

# Print the 30-min price list
print("Current 30-min price list:", prices5Min)

# Extract non-None values from 5-min price list
pricesMeanList = []
for val in prices5Min:
    if val != None:
        pricesMeanList.append(val)

# Calculate the current mean 30-min price
currentPrice30 = mean(pricesMeanList)

# Print the current mean 30-min price
print("Current average 30-min price:", currentPrice30)

# Round currentPrice30 to 2 sig. digits
currentPrice30Rnd = "{:.2f}".format(currentPrice30)

# Define the 5-min alerts function
def alerts5Min():
    # Configure the webhook URL and post data
    webhookUrl = str(os.environ.get('WEBHOOK_URL'))
    priceHigh = float(os.environ.get('PRICE_HIGH'))
    priceLow = float(os.environ.get('PRICE_LOW'))
    priceHighMsg = { "content": "Power price is above " + str(priceHigh) + "c/kWh!\n\nCurrent price is: " + currentPrice5Rnd + "c/kWh.\n\n@everyone" }
    priceLowMsg = { "content": "Power price is below " + str(priceLow) + "c/kWh!\n\nCurrent price is: " + currentPrice5Rnd + "c/kWh.\n\n@everyone" }
    priceNormalMsg = { "content": "Power prices have returned to normal.\n\nCurrent price is: " + currentPrice5Rnd + "c/kWh.\n\n@everyone" }
    priceNegMsg = { "content": "Power prices are negative!\n\nCurrent price is: " + currentPrice5Rnd + "c/kWh.\n\n@everyone" }

    # High price alert
    if currentPrice5 > priceHigh and lastPrice5 <= priceHigh:
        requests.post(webhookUrl, data=priceHighMsg)

    # Low price alert
    if currentPrice5 < priceLow and currentPrice5 >= 0 and lastPrice5 >= priceLow:
        requests.post(webhookUrl, data=priceLowMsg)

    # Return to normal alert
    if currentPrice5 >= priceLow and currentPrice5 <= priceHigh and (lastPrice5 < priceLow or lastPrice5 > priceHigh):
        requests.post(webhookUrl, data=priceNormalMsg)

    # Negative price alert
    if currentPrice5 < 0 and lastPrice5 >= 0:
        requests.post(webhookUrl, data=priceNegMsg)

# Define the 30-min alerts function
def alerts30Min():
    # Configure the webhook URL and post data
    webhookUrl = str(os.environ.get('WEBHOOK_URL'))
    priceHigh = float(os.environ.get('PRICE_HIGH'))
    priceLow = float(os.environ.get('PRICE_LOW'))
    priceHighMsg = { "content": "Power price is above " + str(priceHigh) + "c/kWh!\n\nCurrent price is: " + currentPrice30Rnd + "c/kWh.\n\n@everyone" }
    priceLowMsg = { "content": "Power price is below " + str(priceLow) + "c/kWh!\n\nCurrent price is: " + currentPrice30Rnd + "c/kWh.\n\n@everyone" }
    priceNormalMsg = { "content": "Power prices have returned to normal.\n\nCurrent price is: " + currentPrice30Rnd + "c/kWh.\n\n@everyone" }
    priceNegMsg = { "content": "Power prices are negative!\n\nCurrent price is: " + currentPrice30Rnd + "c/kWh.\n\n@everyone" }

    # High price alert
    if currentPrice30 > priceHigh and lastPrice30 <= priceHigh:
        requests.post(webhookUrl, data=priceHighMsg)

    # Low price alert
    if currentPrice30 < priceLow and currentPrice30 >= 0 and lastPrice30 >= priceLow:
        requests.post(webhookUrl, data=priceLowMsg)

    # Return to normal alert
    if currentPrice30 >= priceLow and currentPrice30 <= priceHigh and (lastPrice30 < priceLow or lastPrice30 > priceHigh):
        requests.post(webhookUrl, data=priceNormalMsg)

    # Negative price alert
    if currentPrice30 < 0 and lastPrice30 >= 0:
        requests.post(webhookUrl, data=priceNegMsg)

# Call the relevant function for 5-min or 30-min price alerts
if os.environ.get('PRICE_TYPE') == "5":
    alerts5Min()
elif os.environ.get('PRICE_TYPE') == "30":
    alerts30Min()
else:
    exit("An incorrect price type has been entered. Please check the value for PRICE_TYPE environment variable and try again.")

# Write the current 5-min price to the pickle file
with open('data/lastprice5.pkl', 'wb') as file:
    pickle.dump(currentPrice5, file)
    file.close()

# Write the current 30-min price to a pickle file
with open('data/lastprice30.pkl', 'wb') as file:
    pickle.dump(currentPrice30, file)
    file.close()

# Write the 30-min price list to the pickle file
with open('data/pricelist30.pkl', 'wb') as file:
    pickle.dump(prices5Min, file)
    file.close()

# Print script completion to log
print("\nScript executed successfully at: " + datetime.strftime(now, "%A %d %b %Y %H:%M:%S") + "\n\n")
