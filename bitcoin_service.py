import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_bitcoin_price():
    """
    Fetches the current Bitcoin price in USD from the CoinGecko API.

    Returns:
        float: The price of Bitcoin in USD, or None if an error occurs.
    """
    try:
        logging.info("Calling Bitcoin API...")
        # Fetch Bitcoin price from CoinGecko API with a timeout
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            timeout=5  # Timeout in seconds
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()

        # Extract and return the Bitcoin price
        return data['bitcoin']['usd']
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while fetching Bitcoin price: {e}")
    except KeyError as e:
        logging.error(f"Unexpected response format: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    # Return None if an error occurs
    return None
