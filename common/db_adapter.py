from common.models.models import db, OhlcvData
import pandas as pd
from sqlalchemy import func



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


def get_latest_data_per_symbol():
    """
    Fetch the latest OHLCV data for each symbol.

    Returns:
        list: A list of dictionaries containing the latest record for each symbol.
    """
    try:
        results = (
            db.session.query(
                OhlcvData.symbol,
                func.max(OhlcvData.open_time).label("latest_open_time")
            )
            .group_by(OhlcvData.symbol)
            .all()
        )

        latest_data = []
        for result in results:
            latest_record = (
                db.session.query(OhlcvData)
                .filter_by(symbol=result.symbol, open_time=result.latest_open_time)
                .first()
            )
            latest_data.append({
                "symbol": result.symbol,
                "open_time": latest_record.open_time,
                "open": latest_record.open,
                "high": latest_record.high,
                "low": latest_record.low,
                "close": latest_record.close,
                "volume": latest_record.volume,
                "close_time": latest_record.close_time,
            })

        return latest_data
    except Exception as e:
        print(f"Error fetching latest data per symbol: {e}")
        return []



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




def get_total_records_per_symbol():
    """
    Fetch the total count of OHLCV records for each symbol.

    Returns:
        list: A list of dictionaries containing the symbol and its total record count.
    """
    try:
        results = (
            db.session.query(
                OhlcvData.symbol,
                func.count(OhlcvData.id).label("total_records")
            )
            .group_by(OhlcvData.symbol)
            .all()
        )

        return [{"symbol": result.symbol, "total_records": result.total_records} for result in results]
    except Exception as e:
        print(f"Error fetching total records per symbol: {e}")
        return []