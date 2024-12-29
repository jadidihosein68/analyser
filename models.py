from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class OhlcvData(db.Model):
    __tablename__ = "ohlcv_data"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    open_time = db.Column(db.BigInteger, nullable=False)
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    close_time = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f"<OhlcvData {self.symbol} @ {self.open_time}>"
