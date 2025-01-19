import pandas as pd
import logging
import talib


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TechnicalIndicatorGenerator:
    def __init__(self, features_config):
        """
        Initialize the Technical Indicator Generator.

        Args:
            features_config (list): List of indicator configurations.
        """
        self.features_config = features_config

    def generate_indicators(self, df):
        """
        Generate technical indicators based on the provided configuration.

        Args:
            df (pd.DataFrame): Dataset with OHLCV columns (open, high, low, close, volume).

        Returns:
            pd.DataFrame: Dataset with additional columns for technical indicators.
        """
        try:
            for feature in self.features_config:
                name = feature["name"]
                params = feature.get("params", {})

                if name == "RSI":
                    df["RSI"] = talib.RSI(df["close"], timeperiod=params["timeperiod"])

                elif name == "MACD":
                    macd, signal, _ = talib.MACD(
                        df["close"],
                        fastperiod=params["fastperiod"],
                        slowperiod=params["slowperiod"],
                        signalperiod=params["signalperiod"]
                    )
                    df["MACD"] = macd
                    df["Signal_Line"] = signal

                elif name == "Simple Moving Average (SMA)":
                    df[f"SMA_{params['window']}"] = talib.SMA(df["close"], timeperiod=params["window"])

                elif name == "Exponential Moving Average (EMA)":
                    df[f"EMA_{params['span']}"] = talib.EMA(df["close"], timeperiod=params["span"])

                elif name == "Average True Range (ATR)":
                    df["ATR"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=params["timeperiod"])

                elif name == "Stochastic Oscillator":
                    slowk, slowd = talib.STOCH(
                        df["high"],
                        df["low"],
                        df["close"],
                        fastk_period=params["fastk_period"],
                        slowk_period=params["slowk_period"],
                        slowk_matype=params["slowk_matype"],
                        slowd_period=params["slowd_period"],
                        slowd_matype=params["slowd_matype"]
                    )
                    df["Stochastic_K"] = slowk
                    df["Stochastic_D"] = slowd

                elif name == "Bollinger Band":
                    upper, middle, lower = talib.BBANDS(
                        df["close"],
                        timeperiod=params["timeperiod"],
                        nbdevup=params["nbdevup"],
                        nbdevdn=params["nbdevdn"],
                        matype=params["matype"]
                    )
                    df["Upper_Band"] = upper
                    df["Middle_Band"] = middle
                    df["Lower_Band"] = lower

                elif name == "Percentage Price Oscillator (PPO)":
                    df["PPO"] = talib.PPO(
                        df["close"],
                        fastperiod=params["fastperiod"],
                        slowperiod=params["slowperiod"],
                        matype=params["matype"]
                    )

                elif name == "Lag Features":
                    for lag in range(1, params["lag_period"] + 1):
                        df[f"close_lag_{lag}"] = df["close"].shift(lag)

            return df.dropna()
        except Exception as e:
            logging.error("Error generating indicators", exc_info=True)
            return None

# Example usage
if __name__ == "__main__":
    # Example dataset
    data = {
        "open": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
        "high": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
        "low": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 25.5,0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 25.5],
        "close": [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 25.5, 26.5,1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 25.5, 26.5],
        "volume": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600,100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600],
    }

    df = pd.DataFrame(data)

    features_config = [
    {
        "name": "RSI",
        "params": {
            "timeperiod": 14
        }
    },
    {
        "name": "MACD",
        "params": {
            "fastperiod": 12,
            "signalperiod": 9,
            "slowperiod": 26
        }
    },
    {
        "name": "Simple Moving Average (SMA)",
        "params": {
            "window": 10
        }
    },
    {
        "name": "Exponential Moving Average (EMA)",
        "params": {
            "span": 10
        }
    },
    {
        "name": "Average True Range (ATR)",
        "params": {
            "timeperiod": 14
        }
    },
    {
        "name": "Stochastic Oscillator",
        "params": {
            "fastk_period": 5,
            "slowd_matype": 0,
            "slowd_period": 3,
            "slowk_matype": 0,
            "slowk_period": 3
        }
    },
    {
        "name": "Bollinger Band",
        "params": {
            "matype": 0,
            "nbdevdn": 2,
            "nbdevup": 2,
            "timeperiod": 20
        }
    },
    {
        "name": "Lag Features",
        "params": {
            "lag_period": 5
        }
    },
    {
        "name": "Percentage Price Oscillator (PPO)",
        "params": {
            "fastperiod": 12,
            "matype": 0,
            "slowperiod": 26
        }
    }
]


    generator = TechnicalIndicatorGenerator(features_config)
    df_with_indicators = generator.generate_indicators(df)
    print(df_with_indicators)
