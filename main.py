from flask import Flask, jsonify
from flask_cors import CORS  # Import Flask-CORS
from common import Config, db
from scheduler.scheduler_service import setup_scheduler
from flask_migrate import Migrate
from routes.ohlcv import ohlcv_bp  
from routes.dataset  import dataset_bp 
from routes.model_config_api  import model_config_bp 

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)


# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})

# Initialize database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Setup the scheduler
# setup_scheduler(app)

# Register Blueprints
app.register_blueprint(ohlcv_bp, url_prefix="/api")
app.register_blueprint(dataset_bp, url_prefix='/api')
app.register_blueprint(model_config_bp, url_prefix='/api')

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
