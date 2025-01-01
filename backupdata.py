import os
import pandas as pd
from common import db, OhlcvData  # Ensure correct imports
from flask import Flask

# Initialize Flask app
app = Flask(__name__)
app.config.from_object("common.config.Config")  # Adjust this to your config path

# Initialize the database
db.init_app(app)

# Path to save the CSV
CSV_FILE_PATH = "ohlcv_data_backup.csv"

def export_to_csv():
    """
    Export all data from the OhlcvData table to a CSV file.
    """
    try:
        with app.app_context():  # Ensure database operations are within the app context
            # Query all records from OhlcvData
            records = db.session.query(OhlcvData).all()

            # Convert to a DataFrame
            df = pd.DataFrame([{
                "id": record.id,
                "symbol": record.symbol,
                "open_time": record.open_time,
                "open": record.open,
                "high": record.high,
                "low": record.low,
                "close": record.close,
                "volume": record.volume,
                "close_time": record.close_time,
            } for record in records])

            # Save to CSV
            df.to_csv(CSV_FILE_PATH, index=False)
            print(f"Data exported successfully to {CSV_FILE_PATH}")
    except Exception as e:
        print(f"Error during export: {e}")

if __name__ == "__main__":
    export_to_csv()
