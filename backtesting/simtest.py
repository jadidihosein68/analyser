import backtrader as bt
import pandas as pd
import joblib
from datetime import datetime
import os

# Configuration
MODEL_DIR = "models"
MODEL_TYPE = "xgboost"
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
        self.signal_counts = {0: 0, 1: 0, 2: 0}

    def next(self):
        # Prepare features for the model using processed indicators
        row = {
            "open": self.data.open[0],
            "high": self.data.high[0],
            "low": self.data.low[0],
            "close": self.data.close[0],
            "volume": self.data.volume[0],
            "RSI_14": self.data.RSI_14[0],
            "MACD": self.data.MACD[0],
            "Signal_Line": self.data.Signal_Line[0],
            "close_lag_1": self.data.close_lag_1[0],
            "close_lag_2": self.data.close_lag_2[0],
            "volume_lag_1": self.data.volume_lag_1[0],
            "volume_lag_2": self.data.volume_lag_2[0]
        }

        # Log features
        print(f"Features: {row}")

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
        if signal == 2 and not self.position:
            # Buy logic
            size = self.broker.get_cash() / self.data.close[0]  # Calculate the number of units to buy
            self.buy(size=size)
            print(f"BUY at {self.data.close[0]} | Cash after BUY: {self.broker.get_cash()} | Position after BUY: {self.position}")
        elif signal == 0 and self.position:
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
    data['datetime'] = pd.to_datetime(data['open_time'], unit='ms')
    data.set_index('datetime', inplace=True)

    # Process DataFrame
    data['RSI_14'] = data['close'].rolling(window=14).apply(
        lambda x: 100 - (100 / (1 + ((x.diff()[x.diff() > 0].sum()) / abs(x.diff()[x.diff() < 0].sum())))) 
        if len(x.dropna()) == 14 and x.diff().sum() != 0 else None
    )

    data['EMA_12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

    data['close_lag_1'] = data['close'].shift(1)
    data['close_lag_2'] = data['close'].shift(2)
    data['volume_lag_1'] = data['volume'].shift(1)
    data['volume_lag_2'] = data['volume'].shift(2)

    # Drop rows with insufficient data
    data.dropna(inplace=True)

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

    # Display final portfolio value
    print(f"Final Portfolio Value: {cerebro.broker.getvalue()}")
