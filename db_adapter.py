from models import db, CryptoPrices

def save_crypto_data(coin_name, price_data):
    """
    Saves cryptocurrency data to the database.

    Args:
        coin_name (str): Name of the cryptocurrency.
        price_data (dict): Dictionary containing value, high, low, close, and open prices.
    """
    crypto_entry = CryptoPrices(
        coin_name=coin_name,
        value=price_data.get("usd"),
        high=price_data.get("usd_24h_high"),
        low=price_data.get("usd_24h_low"),
        close=price_data.get("usd"),  # Assume close = value
        open=price_data.get("usd"),  # Assume open = value
    )
    db.session.add(crypto_entry)
    db.session.commit()
