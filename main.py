from flask import Flask, jsonify
from flask_apscheduler import APScheduler
from datetime import datetime
from scheduler_service import run_scheduled_task

# Define the configuration for the APScheduler
class Config:
    SCHEDULER_API_ENABLED = True  # Enables the APScheduler API


# Create a Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize the APScheduler
scheduler = APScheduler()
scheduler.init_app(app)


# Define a job function
def scheduled_task():
    """
    Executes the scheduled task.
    """
    run_scheduled_task()  # Calls the task logic from scheduler_service.py


# Add the job to the scheduler
scheduler.add_job(
    id="Scheduled Task",
    func=scheduled_task,
    trigger="interval",
    seconds=10,  # Runs every 10 minutes
)


@app.route("/")
def home():
    """
    Home route to indicate the service is running.
    """
    return "Flask app with a job scheduler running!"


@app.route("/health", methods=["GET"])
def health():
    """
    Health check route to confirm the app and scheduler are running.
    """
    return jsonify({"status": "Scheduler is running"}), 200


# Ensure scheduler starts for both flask run and direct execution
def start_scheduler():
    if not scheduler.running:
        scheduler.start()


if __name__ == "__main__":
    start_scheduler()
    app.run(debug=True)
else:
    start_scheduler()