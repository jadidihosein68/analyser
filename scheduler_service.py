from datetime import datetime
from threading import Lock
from bitcoin_service import fetch_bitcoin_price  # Import the function from your service
from db_adapter import save_crypto_data

# Shared dictionary to store the latest Bitcoin price info
latest_bitcoin_price = {"price": None, "timestamp": None}

# Lock to ensure thread safety
job_lock = Lock()

def log_message(level, message):
    """
    Logs a message with a timestamp.

    Args:
        level (str): Log level (INFO, ERROR, etc.)
        message (str): The log message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def fetch_and_update_bitcoin_price():
    """
    Fetches the Bitcoin price using the service and updates the shared variable.
    """
    global latest_bitcoin_price
    with job_lock:
        try:
            log_message("INFO", "Calling Bitcoin API via fetch_bitcoin_price service...")
            bitcoin_price = fetch_bitcoin_price()  # Use the imported service

            if bitcoin_price is not None:
                latest_bitcoin_price["price"] = bitcoin_price
                latest_bitcoin_price["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message("INFO", f"Updated Bitcoin price: ${bitcoin_price}")
            else:
                log_message("WARNING", "Bitcoin price could not be updated (returned None).")
        except Exception as e:
            log_message("ERROR", f"Unexpected error during Bitcoin price update: {e}")


def run_scheduled_task():
    """
    Executes the scheduled task.
    """
    log_message("INFO", "Running scheduled task...")
    fetch_and_update_bitcoin_price()



