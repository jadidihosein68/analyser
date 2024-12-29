from flask_apscheduler import APScheduler
from scheduler_service_tasks import run_scheduled_task

scheduler = APScheduler()

def setup_scheduler(app):
    """
    Initializes and starts the APScheduler, passing the app instance to tasks.
    """
    scheduler.init_app(app)
    scheduler.add_job(
        id="Binance OHLCV Fetcher",
        func=run_scheduled_task,  # Reference the function
        args=[app],  # Pass the app instance as an argument
        trigger="interval",
        seconds=10,  # Fetch data every 10 seconds
    )
    scheduler.start()
