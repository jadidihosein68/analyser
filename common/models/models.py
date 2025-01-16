from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class OhlcvData(db.Model):
    __tablename__ = "ohlcv_data"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    open_time = db.Column(db.BigInteger, nullable=False)
    open = db.Column("open", db.Float, nullable=False)  # Wrap reserved keyword
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column("close", db.Float, nullable=False)  # Wrap reserved keyword
    volume = db.Column(db.Float, nullable=False)
    close_time = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f"<OhlcvData {self.symbol} @ {self.open_time}>"

class OhlcvDataCollection(db.Model):
    __tablename__ = "ohlcv_data_collection"

    id = db.Column(db.Integer, primary_key=True)
    name_of_dataset = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    interval = db.Column(db.String(10), nullable=False)
    startdate = db.Column(db.BigInteger, nullable=False)
    enddate = db.Column(db.BigInteger, nullable=False)
    dataset_type = db.Column(db.String(50), nullable=False)
    total_records = db.Column(db.Integer, nullable=False, default=0)  # New Field

    def __repr__(self):
        return f"<OhlcvDataCollection {self.name_of_dataset} ({self.symbol})>"

class ModelConfig(db.Model):
    __tablename__ = "model_config"

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255), nullable=False)  
    model_type = db.Column(db.String(255), nullable=True)   
    model_config = db.Column(db.JSON, nullable=True)        
    coin_symbol = db.Column(db.String(50), nullable=False)  
    training_dataset_name = db.Column(db.String(255), nullable=False)  
    training_dataset_config = db.Column(db.JSON, nullable=True)  
    features_config = db.Column(db.JSON, nullable=True)     
    physical_location = db.Column(db.String(255), nullable=True)  
    file_name = db.Column(db.String(255), nullable=True)    
    remark = db.Column(db.String(500), nullable=True)       
    accuracy_percent = db.Column(db.Float, nullable=True)   
    date_of_creation = db.Column(db.DateTime, default=datetime.utcnow)  
    label_config = db.Column(db.JSON, nullable=True)        
    status = db.Column(db.String(50), nullable=True)        

    def __repr__(self):
        return f"<ModelConfig {self.model_name}>"