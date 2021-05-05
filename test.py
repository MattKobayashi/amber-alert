from datetime import datetime
from numpy import nan, nanmean
import os
import pickle

# Create pickle file if it doesn't already exist
if not os.path.isfile('last5minprice.pkl'):
    blankPrices5Min = [nan, nan, nan, nan, nan, nan]
    with open('last5minprice.pkl', 'wb') as file:
        pickle.dump(blankPrices5Min, file)
        file.close()

# Read last price from pickle file
with open('last5minprice.pkl', 'rb') as file:
    prices5Min = pickle.load(file)
    file.close()

now = datetime.now()
print("It is currently", now.minute, "minutes past the hour.\n")

currentPrice = 7

if (now.minute >= 0 and now.minute < 5) or (now.minute >= 30 and now.minute < 35):
    prices5Min = [nan, nan, nan, nan, nan, nan]
    prices5Min[0] = currentPrice

if (now.minute >= 5 and now.minute < 10) or (now.minute >= 35 and now.minute < 40):
    prices5Min[1] = currentPrice

if (now.minute >= 10 and now.minute < 15) or (now.minute >= 40 and now.minute < 45):
    prices5Min[2] = currentPrice

if (now.minute >= 15 and now.minute < 20) or (now.minute >= 45 and now.minute < 50):
    prices5Min[3] = currentPrice

if (now.minute >= 20 and now.minute < 25) or (now.minute >= 50 and now.minute < 55):
    prices5Min[4] = currentPrice

if (now.minute >= 25 and now.minute < 30) or (now.minute >= 55 and now.minute < 59):
    prices5Min[5] = currentPrice

price30Min = nanmean(prices5Min)

print("List of 5 minute prices:", prices5Min, "\n")

print("Current average 30 minute price is:", "{:.2f}".format(price30Min), "\n")

# Write the current price to the pickle file
with open('last5minprice.pkl', 'wb') as file:
    pickle.dump(prices5Min, file)
    file.close()

print("\nScript executed successfully at: " + datetime.strftime(now, "%A %d %b %Y %H:%M:%S") + "\n\n")
