import backtrader as bt
import pandas as pd
import joblib
from datetime import datetime
import os
from common import Constants
from training.data_processing import add_technical_indicators
# Configuration
MODEL_DIR = "models"
MODEL_TYPE = "random_forest"
DATA_FILE_PATH = "ohlcv_data_backup.csv"

# Define a custom PandasData class to include additional indicators
class CustomPandasData(bt.feeds.PandasData):
    lines = ('RSI_14', 'MACD', 'Signal_Line', 'close_lag_1', 'close_lag_2', 'volume_lag_1', 'volume_lag_2')
    params = (
        ('RSI_14', None),
        ('MACD', None),
        ('Signal_Line', None),
        ('close_lag_1', None),
        ('close_lag_2', None),
        ('volume_lag_1', None),
        ('volume_lag_2', None),
    )

# Backtrader Strategy
class MLStrategy(bt.Strategy):
    params = (
        ('model_path', os.path.join(MODEL_DIR, f"{MODEL_TYPE}_model.joblib")),
    )

    def __init__(self):
        # Load the pre-trained model
        self.model = joblib.load(self.params.model_path)

        # Signal counters
        self.signal_counts = {
            Constants.SELLSIGNAL: 0,
            Constants.HOLDSIGNAL: 0,
            Constants.BUYSIGNAL: 0
        }

    def next(self):
        # Prepare features for the model using processed indicators
        row = {
            Constants.COLUMN_OPEN: self.data.open[0],
            Constants.COLUMN_HIGH: self.data.high[0],
            Constants.COLUMN_LOW: self.data.low[0],
            Constants.COLUMN_CLOSE: self.data.close[0],
            Constants.COLUMN_VOLUME: self.data.volume[0],
            Constants.COLUMN_RSI_14: self.data.RSI_14[0],
            Constants.COLUMN_MACD: self.data.MACD[0],
            Constants.COLUMN_SIGNAL_LINE: self.data.Signal_Line[0],
            Constants.COLUMN_CLOSE_LAG_1: self.data.close_lag_1[0],
            Constants.COLUMN_CLOSE_LAG_2: self.data.close_lag_2[0],
            Constants.COLUMN_VOLUME_LAG_1: self.data.volume_lag_1[0],
            Constants.COLUMN_VOLUME_LAG_2: self.data.volume_lag_2[0]
        }

        # Log features
        #print(f"Features: {row}")

        # Check for missing data
        if any(v is None for v in row.values()):
            print("Skipping due to missing data")
            return

        # Convert to DataFrame for prediction
        feature_columns = ["open", "high", "low", "close", "volume", "RSI_14", "MACD", "Signal_Line", 
                           "close_lag_1", "close_lag_2", "volume_lag_1", "volume_lag_2"]
        features = pd.DataFrame([row])[feature_columns]

        # Predict trading signal
        signal = self.model.predict(features)[0]
        self.signal_counts[signal] += 1  # Count the signal
        print(f"Predicted Signal: {signal}, Position: {self.position}, Cash: {self.broker.get_cash()}")

        # Execute buy/sell based on the signal
        if signal == Constants.BUYSIGNAL and not self.position:
            # Buy logic
            size = self.broker.get_cash() / self.data.close[0]  # Calculate the number of units to buy
            self.buy(size=size)
            print(f"BUY at {self.data.close[0]} | Cash after BUY: {self.broker.get_cash()} | Position after BUY: {self.position}")
        elif signal == Constants.SELLSIGNAL and self.position:
            # Sell logic
            self.sell(size=self.position.size)  # Sell the entire position
            print(f"SELL at {self.data.close[0]} | Cash after SELL: {self.broker.get_cash()} | Position after SELL: {self.position}")

    def stop(self):
        # Print signal counts at the end of the strategy
        print("Signal Counts:", self.signal_counts)

# Main Execution
if __name__ == "__main__":
    # Load OHLCV data
    data = pd.read_csv(DATA_FILE_PATH)
    data['datetime'] = pd.to_datetime(data[Constants.COLUMN_CLOSE_TIME], unit='ms')
    data.set_index('datetime', inplace=True)
    
    data = add_technical_indicators(data)

    if data is None or data.empty:
        print("Error: No valid data after adding technical indicators.")
    else:
        # Backtrader Data Feed
        data_feed = CustomPandasData(
            dataname=data,
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
            RSI_14='RSI_14',
            MACD='MACD',
            Signal_Line='Signal_Line',
            close_lag_1='close_lag_1',
            close_lag_2='close_lag_2',
            volume_lag_1='volume_lag_1',
            volume_lag_2='volume_lag_2'
        )

    # Initialize Backtrader Engine
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(MLStrategy)
    cerebro.broker.set_cash(10000)  # Initial cash
    cerebro.run()
    cerebro.plot()

    # Display final portfolio value
    print(f"Final Portfolio Value: {cerebro.broker.getvalue()}")
