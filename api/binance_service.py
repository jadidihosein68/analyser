import requests
import logging

logging.basicConfig(level=logging.INFO)

def fetch_ohlcv_data(symbol, interval="1m", limit=5):
    """
    Fetches OHLCV data from Binance for a given trading pair.

    Args:
        symbol (str): The trading pair (e.g., "BTCUSDT").
        interval (str): The interval for candlestick data (default: "1m").
        limit (int): Number of candlesticks to fetch (default: 5).

    Returns:
        list: A list of dictionaries containing OHLCV data.
    """
    try:
        logging.info(f"Fetching OHLCV data for symbol: {symbol}, interval: {interval}, limit: {limit}")
        
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        raw_data = response.json()
        ohlcv_data = [
            {
                "open_time": entry[0],
                "open": entry[1],
                "high": entry[2],
                "low": entry[3],
                "close": entry[4],
                "volume": entry[5],
                "close_time": entry[6],
            }
            for entry in raw_data
        ]
        
        return ohlcv_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching OHLCV data for {symbol}: {e}")
    return None
