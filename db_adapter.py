from models import db, OhlcvData
import pandas as pd


def save_ohlcv_data(symbol, ohlcv_entry):
    """
    Saves OHLCV data to the database using the ORM.

    Args:
        symbol (str): The trading pair (e.g., "BTCUSDT").
        ohlcv_entry (dict): Dictionary containing OHLCV data.
    """
    try:
        ohlcv_data = OhlcvData(
            symbol=symbol,
            open_time=ohlcv_entry["open_time"],
            open=ohlcv_entry["open"],
            high=ohlcv_entry["high"],
            low=ohlcv_entry["low"],
            close=ohlcv_entry["close"],
            volume=ohlcv_entry["volume"],
            close_time=ohlcv_entry["close_time"],
        )
        db.session.add(ohlcv_data)
        db.session.commit()
    except Exception as e:
        print(f"Error saving OHLCV data for {symbol}: {e}")
        db.session.rollback()

def get_all_ohlcv_data():
    """
    Retrieve all OHLCV data from the database and return it as a Pandas DataFrame.
    """
    try:
        query = db.session.query(OhlcvData).all()
        data = [
            {
                "open_time": entry.open_time,
                "open": entry.open,
                "high": entry.high,
                "low": entry.low,
                "close": entry.close,
                "volume": entry.volume,
                "close_time": entry.close_time,
            }
            for entry in query
        ]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error retrieving data from database: {e}")
        return None
