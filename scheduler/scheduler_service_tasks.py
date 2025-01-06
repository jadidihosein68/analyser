from api.binance_service import fetch_ohlcv_data
from common import Config, db, get_all_ohlcv_data, save_ohlcv_data, Constants

def run_scheduled_task(app):
    """
    Executes the scheduled task to fetch and store Binance OHLCV data.
    Ensures the task runs within the Flask app context.
    """
    with app.app_context():  # Explicitly use the Flask application context
        symbol = Constants.BTCUSDT  # Bitcoin to USD Tether
        interval = "5m"  # 1-minute interval
        limit = 1 # Fetch the last 5 candlesticks each 300 is almost 1 day and max is 1000 

        print("Running scheduled task...")
        ohlcv_data = fetch_ohlcv_data(symbol, interval, limit)

        if ohlcv_data:
            print(ohlcv_data)
            for entry in ohlcv_data:
                save_ohlcv_data(symbol, entry)  # Save data to the database
        else:
            print("Failed to fetch OHLCV data.")
