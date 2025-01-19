# Glossary : 

Term | Meaning 
--- | --- 
bullish | market is bullish (going up) 
bear  | In a bear market (going down)
sideways | stable markets
regimes | different market conditions (bullish, bear or sideways )



# Strategy

Summary
Data Collection: Connect to Binance’s API (via python-binance or ccxt) to fetch intraday (1–5 min) OHLCV data.
Data Prep: Clean data, handle missing values, and focus on essential columns (OHLC + volume).
Feature Engineering: Add indicators (moving averages, RSI, etc.).
Model: Train a Random Forest or XGBoost model (classification or regression).
Backtest: Assess your strategy’s profitability on historical data.
Paper Trade / Live: Use the model’s predictions in near real-time and simulate or place trades on Binance.
Iterate: Continuously refine your features, model parameters, and risk management rules.
This end-to-end outline will help you build a basic crypto prediction application in Python and then expand it over time (adding more sophisticated features, improved models, etc.). Always remember: no model guarantees profit, and it’s crucial to thoroughly test and manage risk before trading real money.


We focuse on binance only. 


A practical approach for many intraday traders is to start with 3–6 months of data and then extend to 12 months as your model matures.



Avoid “One-Size-Fits-All” Overfitting

A single model might struggle to learn the drastically different patterns of up, down, and sideways markets all at once.
Splitting data into regime-specific models reduces noise—each model only sees data that is relevant to its particular scenario.



Historical Data Mismatch

If you train on a bull cycle but apply to a current bull cycle that’s far more extreme, the historical bull data might not fully represent today’s market. The same goes for bear or sideways conditions.
Having separate models for each regime can help isolate these issues.





2. How Frequent Should the Interval Be?
(a) Common Bar Intervals for Intraday
1-minute bars
Pros: Most granular; captures micro-movements.
Cons: Highly noisy, large dataset to store and process, more frequent trades (potentially higher fees).
5-minute bars
A popular balance between detail and noise.
Good for short-term patterns without being overwhelmed by microsecond fluctuations.
15-minute or 30-minute bars
Smoother trends, less “noise,” fewer trades.
You might miss very short-lived opportunities.


Most traders new to intraday trading often start with 5-minute intervals to capture quick moves without drowning in too much noise.

(lets go with 5 min)






Research & Strategy Formulation: Decide on technical (e.g., momentum, mean reversion) or fundamental analysis (e.g., news sentiment) or a combination.
Technical Indicators: Incorporate common indicators or custom signals (MA, RSI, MACD, Bollinger Bands, etc.).





Trading Objectives: Identify whether the bot will focus on short-term scalping, long-term investing, or arbitrage.
Risk Tolerance: Determine maximum drawdown, position sizing, and how you’ll manage volatility.
Time Horizon: Choose whether the bot will trade continuously, daily, or based on specific market conditions.
Budget & Resources: Estimate costs for development, infrastructure (servers, APIs), and ongoing maintenance.
Portfolio Management: Track positions, balances, and overall performance.

find regime ! 

Error handling and fallback mechanisms (in case of exchange downtime).
Logging and monitoring solutions.


Risk Management:
   Position sizing (e.g., fixed fraction of capital).
   Stop-loss and take-profit thresholds.
   Maximum daily drawdown or maximum position size constraints.


Backtest Engine: Use historical data to simulate your strategy’s performance.
Performance Metrics: Track metrics like CAGR (compound annual growth rate), Sharpe ratio, maximum drawdown.
Refine Strategy: Identify any weaknesses, adjust parameters, or switch to different indicators if needed.
Paper Trading: Run the bot in a simulated or testnet environment, where no real money is at risk.



Performance Tracking: Monitor PnL (profit and loss), daily returns, trades executed, etc.
Evaluate performance metrics (PnL, Sharpe, drawdown, etc.) to decide if the strategy is viable.

Risk Management Updates: Adjust position sizing, stop-losses, or other risk parameters as market conditions change.

Regular Strategy Evaluation: Market conditions change rapidly—evaluate your bot’s strategy on a periodic basis to ensure it remains profitable.

New Features: Add advanced functionalities like sentiment analysis, machine learning models, or specialized indicators.
Multi-Exchange or Multi-Asset: Expand to more trading pairs, different cryptocurrencies, or even different asset classes if relevant.
Continuous Improvement: Apply lessons learned from live trading data to refine strategy logic, reduce slippage, and optimize execution.





Step-by-Step Overview
Label Each Historical Bar with a Regime

Using your chosen rule (e.g., 200-day MA) or advanced method, annotate each data point as “bull,” “bear,” or “sideways.”
Split the Historical Data

Create three subsets of data: one for bull times, one for bear times, one for sideways times.
Train a Separate Model

Model A (Bull Model): Trained only on bull data.
Model B (Bear Model): Trained only on bear data.
Model C (Sideways Model): Trained only on sideways data.
Live/Real-Time Predicting

Detect Current Regime: At each new time step, figure out if we’re in a bull, bear, or sideways period.
Use the Corresponding Model: If it’s bull → use Model A’s predictions; if bear → Model B; if sideways → Model C.
Transition Handling

Markets can switch regimes quickly, so keep your detection logic updated.
You might add a “grace period” to confirm a new regime before switching the model.




# Binance API 


binance info : 

HTTP 429 return code is used when breaking a request rate limit.
HTTP 418 return code is used when an IP has been auto-banned for continuing to send requests after receiving 429 codes.
HTTP 5XX return codes are used for internal errors; the issue is on Binance's side. It is important to NOT treat this as a failure operation; the execution status is UNKNOWN and could have been a success.



Request : 



Respond :
reference https://developers.binance.com/docs/derivatives/coin-margined-futures/market-data/Kline-Candlestick-Data

```json
[
  [
    1591258320000,      	// Open time
    "9640.7",       	 	// Open
    "9642.4",       	 	// High
    "9640.6",       	 	// Low
    "9642.0",      	 	 	// Close (or latest price)
    "206", 			 		// Volume
    1591258379999,       	// Close time
    "2.13660389",    		// Base asset volume
    48,             		// Number of trades
    "119",    				// Taker buy volume
    "1.23424865",      		// Taker buy base asset volume
    "0" 					// Ignore.
  ]
]

```






# Requirement


Identify Market Regimes 

Moving Average Trend Rule : 
(tag long term MACD can be 200 days etc ask chat gpt) identify if it is bull ( current price is above a certain long-term moving average (e.g., 200-day MA) by a threshold) or bear (current price is below by a threshold)

Price Change Over X Days
Look at percentage change in price over a recent window (e.g., 30 days). If it’s strongly positive → bull, strongly negative → bear, small → sideways.

Volatility-Based
Use a volatility measure (e.g., Bollinger Bands, ATR) to detect if the market is choppy but not trending vs. trending strongly.







Split the Historical Data

Create three subsets of data: one for bull times, one for bear times, one for sideways times.
Train a Separate Model

Model A (Bull Model): Trained only on bull data.
Model B (Bear Model): Trained only on bear data.
Model C (Sideways Model): Trained only on sideways data.



Live/Real-Time Predicting

Detect Current Regime: At each new time step, figure out if we’re in a bull, bear, or sideways period.
Use the Corresponding Model: If it’s bull → use Model A’s predictions; if bear → Model B; if sideways → Model C.




Transition Handling

Markets can switch regimes quickly, so keep your detection logic updated.
You might add a “grace period” to confirm a new regime before switching the model.







# Project Overview

This project is designed for trading simulation and prediction using machine learning models on OHLCV (Open, High, Low, Close, Volume) data. The system supports real-time data handling, model training, and strategy backtesting using Backtrader.

## Folder Structure

### Root Files
- **README.md**: Documentation of the project.
- **requirements.txt**: Python dependencies for the project.
- **.gitignore**: Specifies files and folders to ignore in version control.

### Data Management
- **binance_service.py**: Handles data fetching from Binance API.
- **db_adapter.py**: Manages database interactions for saving and retrieving OHLCV data.
- **backupdata.py**: Responsible for backing up data for recovery and testing purposes.

### Core Functionality
- **data_processing.py**: Provides functions for cleaning, preprocessing, and adding technical indicators to the data.
- **labeling.py**: Implements labeling logic for training, such as determining buy, sell, or hold signals based on future price movements.
- **model_training.py**: Handles the training and saving of machine learning models (e.g., Random Forest, XGBoost).
- **realtime_prediction.py**: Performs real-time predictions using trained models on live data.
- **process_dataframe.py**: Contains utility functions for processing data, such as handling missing values and standardizing formats.

### Application
- **main.py**: Entry point for the web application, handling routes and managing the Flask app lifecycle.
- **config.py**: Configuration file for database connections, API keys, and other environment variables.
- **models.py**: Defines database models and schemas for handling data storage.
- **scheduler_service.py**: Manages background jobs and periodic tasks for fetching data and making predictions.
- **scheduler_service_tasks.py**: Contains the individual tasks executed by the scheduler, such as data fetch or model retrain.

### Backtesting and Simulation
- **simtest.py**: Executes a Backtrader simulation using trained models and historical data.
- **main_predict.py**: Centralized script for running predictions and simulations based on processed data.

### Tests
- **tests/**: Contains unit and integration tests for various components (to be developed).

## Key Features
- **Real-Time Predictions**: Fetch live OHLCV data, preprocess it, and predict signals using machine learning models.
- **Backtesting**: Test different strategies using historical data to evaluate performance.
- **Machine Learning Integration**: Train and save models to predict buy/sell/hold signals based on labeled data.
- **Data Management**: Store and manage historical and live data in a structured database.
- **Scheduler**: Automate data fetching and processing at periodic intervals.

## Getting Started

### Prerequisites
- Python 3.8+
- Install dependencies using:
  ```bash
  pip install -r requirements.txt
  ```

### Usage
1. **Fetch Data**:
   Use `binance_service.py` to fetch OHLCV data.

2. **Process Data**:
   Run `data_processing.py` to clean and enhance data with technical indicators.

3. **Label Data**:
   Use `labeling.py` to generate labels for training.

4. **Train Models**:
   Train machine learning models using `model_training.py`.

5. **Run Simulation**:
   Execute `simtest.py` to backtest strategies with trained models.

6. **Real-Time Predictions**:
   Deploy the Flask app using `main.py` to fetch live data and predict signals.

## Contributing
- Open to improvements and contributions.
- Submit issues or pull requests for discussions.

## License
This project is licensed under the MIT License.



Roadmap : 

1- Use TA-Lib for timeseries 
2- use Freqtrade for backtesting paper traiding and real live traiding  



to run the application make sure to run the migration : 
flask db upgrade

make sure to install TA-LIB from official (Python PiP may not work)
https://ta-lib.org/install/#linux-build-from-source

