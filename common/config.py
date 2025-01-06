from sqlalchemy.engine import URL

class Config:
    SQLALCHEMY_DATABASE_URI = URL.create(
        "mssql+pyodbc",
        query={
            "odbc_connect": (
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=DESKTOP-BV0EM2G;"
                "Database=traider;"
                "Trusted_Connection=yes;"
            )
        }
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
    class Binance:
        # Binance API
        BINANCE_PUBLIC_OHLCV = "https://api.binance.com/api/v3/klines"