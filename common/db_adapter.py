from common.models.models import db, OhlcvData, OhlcvDataCollection, ModelConfig
import pandas as pd
from sqlalchemy import func, and_


def get_ohlcv_records_by_interval(symbol, start_close_time, end_close_time, interval):
    """
    Fetch records for a symbol within a specified close time range, based on the interval.

    Args:
        symbol (str): The trading pair symbol.
        start_close_time (int): Start close time in epoch.
        end_close_time (int): End close time in epoch.
        interval (int): Interval in minutes (0 means no filtering by interval).

    Returns:
        list: Records that match the conditions.
    """
    try:
        query = db.session.query(OhlcvData).filter(
            and_(
                OhlcvData.symbol == symbol,
                OhlcvData.close_time >= start_close_time,
                OhlcvData.close_time <= end_close_time,
            )
        )

        if interval > 0:
            interval_ms = interval * 60 * 1000  # Convert minutes to milliseconds
            query = query.filter(
                (OhlcvData.close_time - start_close_time) % interval_ms == 0
            )

        return query.all()
    except Exception as e:
        print(f"Error fetching OHLCV records by interval: {e}")
        return []

def count_ohlcv_records_by_interval(symbol, start_close_time, end_close_time, interval):
    """
    Count records for a symbol within a specified close time range, based on the interval.

    Args:
        symbol (str): The trading pair symbol.
        start_close_time (int): Start close time in epoch.
        end_close_time (int): End close time in epoch.
        interval (int): Interval in minutes (0 means no filtering by interval).

    Returns:
        int: Count of records that match the conditions.
    """
    try:
        records = get_ohlcv_records_by_interval(symbol, start_close_time, end_close_time, interval)
        return len(records)
    except Exception as e:
        print(f"Error counting OHLCV records by interval: {e}")
        return 0

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

def save_ohlcv_data_collection(name_of_dataset, symbol, interval, startdate, enddate, dataset_type,total_records):
    try:
        data_entry = OhlcvDataCollection(
            name_of_dataset=name_of_dataset,
            symbol=symbol,
            interval=interval,
            startdate=startdate,
            enddate=enddate,
            dataset_type=dataset_type,
            total_records=total_records
        )
        db.session.add(data_entry)
        db.session.commit()
    except Exception as e:
        print(f"Error saving OHLCV data collection: {e}")
        db.session.rollback()

def get_ohlcv_data_collections():
    try:
        return OhlcvDataCollection.query.all()
    except Exception as e:
        print(f"Error fetching OHLCV data collections: {e}")
        return []


def create_model_config(data):
    """
    Save a new model config to the database.

    Args:
        data (dict): A dictionary containing model config data.
    Returns:
        ModelConfig: The created model config.
    """
    try:
        model_config = ModelConfig(**data)
        db.session.add(model_config)
        db.session.commit()
        return model_config
    except Exception as e:
        db.session.rollback()
        print(f"Error creating model config: {e}")
        raise e

def get_model_config_by_id(config_id):
    """
    Retrieve a model config by ID.

    Args:
        config_id (int): The ID of the model config.
    Returns:
        ModelConfig: The retrieved model config, or None if not found.
    """
    try:
        return ModelConfig.query.get(config_id)
    except Exception as e:
        print(f"Error fetching model config by ID: {e}")
        raise e

def list_model_configs():
    """
    Retrieve all model configs.

    Returns:
        list: A list of ModelConfig objects.
    """
    try:
        return ModelConfig.query.all()
    except Exception as e:
        print(f"Error fetching all model configs: {e}")
        raise e

def update_model_config(config_id, data):
    """
    Update a model config by ID.

    Args:
        config_id (int): The ID of the model config.
        data (dict): A dictionary containing the updated model config data.
    Returns:
        ModelConfig: The updated model config, or None if not found.
    """
    try:
        model_config = ModelConfig.query.get(config_id)
        if not model_config:
            return None
        for key, value in data.items():
            if hasattr(model_config, key):
                setattr(model_config, key, value)
        db.session.commit()
        return model_config
    except Exception as e:
        db.session.rollback()
        print(f"Error updating model config: {e}")
        raise e

def delete_model_config(config_id):
    """
    Delete a model config by ID.

    Args:
        config_id (int): The ID of the model config.
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        model_config = ModelConfig.query.get(config_id)
        if not model_config:
            return False
        db.session.delete(model_config)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting model config: {e}")
        raise e

def update_label_config(config_id, label_config):
    """
    Update the label_config field for a specific model config by ID.

    Args:
        config_id (int): The ID of the model config.
        label_config (dict): The new label_config object.

    Returns:
        ModelConfig: The updated model config.
    """
    try:
        model_config = ModelConfig.query.get(config_id)
        if not model_config:
            return None
        model_config.label_config = label_config
        db.session.commit()
        return model_config
    except Exception as e:
        db.session.rollback()
        raise e

def update_model_fields(config_id, model_config=None):
    """
    Update fields for a specific model config by ID.

    Args:
        config_id (int): The ID of the model config.
        model_config (dict): The new model_config JSON object (optional).

    Returns:
        ModelConfig: The updated model config, or None if not found.
    """
    try:
        model_config_obj = ModelConfig.query.get(config_id)
        if not model_config_obj:
            return None

        # Update fields
        if model_config is not None:
            model_config_obj.model_config = model_config

        db.session.commit()
        return model_config_obj
    except Exception as e:
        db.session.rollback()
        raise e