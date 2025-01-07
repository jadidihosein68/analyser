import backtrader as bt
import pandas as pd
import joblib
from datetime import datetime
import os
import csv
from common import Constants
from training.data_processing import add_technical_indicators
from common.position_sizing import PositionSizing

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

        # Store completed trades
        self.deals = []
        self.last_executed_size = 0.0  # Track the executed size
        self.buy_price = None  # Track the buy price
        self.sell_price = None  # Track the sell price

        # Position Sizing Setup
        self.position_sizer = PositionSizing(account_balance=10000, risk_per_trade=0.02)

        # Track portfolio state
        self.total_assets = 0.0
        self.cash = self.broker.get_cash()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f"BUY EXECUTED: Price: {order.executed.price}, Size: {order.executed.size}, Cash: {self.broker.get_cash()}")
                self.buy_price = order.executed.price
                self.total_assets += order.executed.size
                self.cash = self.broker.get_cash()
            elif order.issell():
                print(f"SELL EXECUTED: Price: {order.executed.price}, Size: {order.executed.size}, Cash: {self.broker.get_cash()}")
                self.sell_price = order.executed.price
                self.total_assets -= order.executed.size
                self.cash = self.broker.get_cash()
            # Track the executed size
            self.last_executed_size = order.executed.size
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f"Order Failed: {order.status}")

    def notify_trade(self, trade):
        if trade.isclosed:
            trade_type = "BUY" if self.sell_price is None else "SELL"
            buy_price = self.buy_price if trade_type == "BUY" else None
            sell_price = self.sell_price if trade_type == "SELL" else None
            profit = trade.pnlcomm
            cash_before = self.broker.get_cash() + profit  # Cash before this trade
            cash_after = self.broker.get_cash()  # Cash after this trade
            portfolio_value = cash_after + (self.total_assets * self.data.close[0])  # Total portfolio value

            # Use the last executed size
            size = abs(getattr(self, "last_executed_size", 0.0))

            # Calculate cumulative profit
            cumulative_profit = sum([d['Profit'] for d in self.deals]) + profit

            # Append trade details
            self.deals.append({
                'Trade Type': trade_type,
                'Buy Price': buy_price,
                'Sell Price': sell_price,
                'Open Price': self.data.open[0],
                'Close Price': self.data.close[0],
                'Size Bought': size,
                'Profit': profit,
                'Cash Before Trade': cash_before,
                'Cash After Trade': cash_after,
                'Assets Held After Trade': self.total_assets,
                'Cumulative Profit': cumulative_profit,
                'Portfolio Value After Trade': portfolio_value,
                'Signal': trade_type,
                'Reason': f"{trade_type} triggered by model"
            })

            print(f"TRADE CLOSED: Type: {trade_type}, Buy: {buy_price}, Sell: {sell_price}, Open: {self.data.open[0]}, "
                f"Close: {self.data.close[0]}, Size: {size}, Profit: {profit}, Cash Before: {cash_before}, "
                f"Cash After: {cash_after}, Portfolio Value: {portfolio_value}")

            # Reset buy and sell prices after the trade is closed
            self.buy_price = None
            self.sell_price = None  
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

        # Debug signals
        print(f"Row: {row}")

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
        print(f"Predicted Signal: {signal}")
        self.signal_counts[signal] += 1

        # Execute buy/sell based on the signal
        if signal == Constants.BUYSIGNAL:
            if self.broker.get_cash() > 0:
                close_price = self.data.close[0]
                reward_to_risk_ratio = 2.0  # Example: Reward is twice the risk
                win_rate = 0.6  # Example: 60% chance of winning

                try:
                    size = self.position_sizer.calculate_position_size(
                        method='kelly',
                        win_rate=win_rate,
                        reward_to_risk_ratio=reward_to_risk_ratio
                    )
                    if self.broker.get_cash() >= size:
                        print(f"Executing BUY: Size: {size}, Price: {close_price}, Cash Before: {self.broker.get_cash()}")
                        self.buy(size=size / close_price)  # Convert size to units
                    else:
                        print("Not enough cash to execute BUY.")
                except ValueError as e:
                    print(f"Error in position sizing: {e}")

        elif signal == Constants.SELLSIGNAL and self.total_assets > 0:
            print(f"Executing SELL: Size: {self.position.size}, Price: {self.data.close[0]}, Cash Before: {self.broker.get_cash()}")
            self.sell(size=self.position.size)

        elif signal == Constants.HOLDSIGNAL:
            print("HOLD Signal: No action taken.")
    def stop(self):
        # Save completed trades to CSV
        output_file = "completed_trades.csv"
        keys = ['Trade Type', 'Buy Price', 'Sell Price', 'Open Price', 'Close Price', 'Size Bought', 'Profit', 'Cash Before Trade', 'Cash After Trade', 'Assets Held After Trade', 'Cumulative Profit', 'Portfolio Value After Trade', 'Signal', 'Reason']
        if not self.deals:
            print("No completed trades to save.")
        else:
            with open(output_file, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.deals)

            print(f"Completed trades saved to {output_file}")
        print("Signal Counts:", self.signal_counts)

# Main Execution
if __name__ == "__main__":
    # Load OHLCV data
    data = pd.read_csv(DATA_FILE_PATH)
    data['datetime'] = pd.to_datetime(data[Constants.COLUMN_CLOSE_TIME], unit='ms')
    data.set_index('datetime', inplace=True)

    # Add technical indicators
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
        cerebro.broker.setcommission(commission=0.001)  # Binance commission: 0.10%
        cerebro.run()

        # Display final portfolio value
        print(f"Final Portfolio Value: {cerebro.broker.getvalue()}")
