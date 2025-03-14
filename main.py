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


def main():
    # Create price data JSON file if it doesn't already exist
    if not os.path.isfile("data/price_data.json"):
        blank_price = {"last_price": 0}
        with open("data/price_data.json", "w", encoding="utf-8") as file:
            json.dump(blank_price, file)

    # Read price data from JSON file
    with open("data/price_data.json", "r", encoding="utf-8") as file:
        price_data_file = json.load(file)

    # Get the current datetime
    now = datetime.now()

    # Load environment variables
    try:
        with open("/run/secrets/AMBER_API_KEY", "r", encoding="utf-8") as api_key_secret:
            api_key = api_key_secret.read().strip()
    except FileNotFoundError as e:
        raise Exception("API key secret not defined.") from e
    except Exception as e:
        raise Exception(f"Error reading API key secret: {e}") from e

    try:
        site_id = os.environ["AMBER_SITE_ID"]
        webhook_url = os.environ["WEBHOOK_URL"]
        alert_high = float(os.environ["ALERT_HIGH"])
        alert_low = float(os.environ["ALERT_LOW"])
        price_res = os.environ["DATA_RES"]
    except KeyError as e:
        raise Exception(f"Missing environment variable: {e}") from e
    except ValueError as e:
        raise Exception(f"Invalid value for environment variable: {e}") from e

    # Set the URL for the Amber Electric API
    api_url = (
        f"https://api.amber.com.au/v1/sites/{site_id}/prices/current?resolution={price_res}"
    )

    # Get current price data from the API and parse the JSON
    try:
        api_response = requests.get(
            api_url,
            headers={"accept": "application/json", "Authorization": f"Bearer {api_key}"}
        )
        api_response.raise_for_status()
        price_data_api = api_response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}") from e

    # Set variables
    current_price = float(price_data_api[0]["perKwh"])
    current_price_rnd = "{:.2f}".format(current_price)
    last_price = float(price_data_file["last_price"])

    # Print last price
    print("Last price:", last_price)
    print("Current price:", current_price)

    # Alert message strings
    alert_high_msg = {
        "content": "Power price is above "
        + str(alert_high)
        + "c/kWh!\n\nCurrent price is: "
        + str(current_price_rnd)
        + "c/kWh.\n\n@everyone"
    }
    alert_low_msg = {
        "content": "Power price is below "
        + str(alert_low)
        + "c/kWh!\n\nCurrent price is: "
        + str(current_price_rnd)
        + "c/kWh.\n\n@everyone"
    }
    alert_normal_msg = {
        "content": "Power prices have returned to normal.\n\nCurrent price is: "
        + str(current_price_rnd)
        + "c/kWh.\n\n@everyone"
    }
    alert_neg_msg = {
        "content": "Power prices are negative!\n\nCurrent price is: "
        + str(current_price_rnd)
        + "c/kWh.\n\n@everyone"
    }

    # High price alert
    if current_price > alert_high and last_price <= alert_high:
        requests.post(webhook_url, data=alert_high_msg)

    # Low price alert
    if current_price < alert_low and current_price >= 0 and last_price >= alert_low:
        requests.post(webhook_url, data=alert_low_msg)

    # Return to normal alert
    if (
        current_price >= alert_low
        and current_price <= alert_high
        and (last_price < alert_low or last_price > alert_high)
    ):
        requests.post(webhook_url, data=alert_normal_msg)

    # Negative price alert
    if current_price < 0 and last_price >= 0:
        requests.post(webhook_url, data=alert_neg_msg)

    # Update the last prices to match the current ones
    price_data_file["last_price"] = current_price

    # Write updated price data to the JSON file
    with open("data/price_data.json", "w", encoding="utf-8") as file:
        json.dump(price_data_file, file)
        file.close()

    # Print script completion to log
    print(
        "\nScript executed successfully at: "
        + datetime.strftime(now, "%A %d %b %Y %H:%M:%S")
        + "\n\n"
    )


if __name__ == "__main__":
    main()
