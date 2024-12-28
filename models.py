from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CryptoPrices(db.Model):
    __tablename__ = "crypto_prices"

    id = db.Column(db.Integer, primary_key=True)
    coin_name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    value = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=True)
    low = db.Column(db.Float, nullable=True)
    close = db.Column(db.Float, nullable=True)
    open = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<CryptoPrices {self.coin_name} @ {self.date}>"
