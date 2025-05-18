from apscheduler.schedulers.blocking import BlockingScheduler
from app import create_app
from app.utils.scheduler import run_weather_check

app = create_app()
scheduler = BlockingScheduler()

# @scheduler.scheduled_job('cron', hour=6, minute=0)
# def scheduled_task():
#     print("[🕕] Weather task started 6h.")
#     run_weather_check(app)
#     print("[✅] Weather task completed.\n")

# Run every minute (for testing)

@scheduler.scheduled_job('cron', minute='*/1')
def scheduled_task():
    print("[🕕] Weather task started (testing every minute).")
    run_weather_check(app)
    print("[✅] Weather task completed.\n")

if __name__ == '__main__':
    # Run the task immediately for testing
    print("[⏳] Immediate execution of weather task for testing.")
    run_weather_check(app)
    print("[✅] Immediate execution completed.\n")

    try:
        print("[🚀] Scheduler started. Waiting for the next execution.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[🛑] Scheduler stopped.")
