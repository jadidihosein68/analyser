from flask import Flask, jsonify
from common import Config, db
from scheduler_service import setup_scheduler
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Setup the scheduler
setup_scheduler(app)

@app.route("/")
def home():
    """
    Home route to indicate the service is running.
    """
    return "Flask app with a Binance OHLCV data scheduler running!"

@app.route("/health", methods=["GET"])
def health():
    """
    Health check route to confirm the app and scheduler are running.
    """
    return jsonify({"status": "Scheduler is running"}), 200

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
