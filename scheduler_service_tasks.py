from binance_service import fetch_ohlcv_data
from db_adapter import save_ohlcv_data

def run_scheduled_task(app):
    """
    Executes the scheduled task to fetch and store Binance OHLCV data.
    Ensures the task runs within the Flask app context.
    """
    with app.app_context():  # Explicitly use the Flask application context
        symbol = "BTCUSDT"  # Bitcoin to USD Tether
        interval = "5m"  # 1-minute interval
        limit = 300  # Fetch the last 5 candlesticks

        print("Running scheduled task...")
        ohlcv_data = fetch_ohlcv_data(symbol, interval, limit)

        if ohlcv_data:
            print(ohlcv_data)
            for entry in ohlcv_data:
                save_ohlcv_data(symbol, entry)  # Save data to the database
        else:
            print("Failed to fetch OHLCV data.")
