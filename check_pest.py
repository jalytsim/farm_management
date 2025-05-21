from apscheduler.schedulers.blocking import BlockingScheduler
from app.utils.schedulerpest import run_gdd_pest_check
from app import create_app

app = create_app()
scheduler = BlockingScheduler()

# @scheduler.scheduled_job('cron', minute='*/1')  # Exécution toutes les 5 minutes (modifie selon ton besoin)
# def scheduled_task():
#     print("[🕕] GDD Pest alert task started.")
#     run_gdd_pest_check(app)
#     print("[✅] GDD Pest task completed.\n")

@scheduler.scheduled_job('cron', hour=6, minute=0)
def scheduled_task():
    print("[🕕] Weather and GDD Pest alert task started 6h.")
    run_gdd_pest_check(app)
    # run_gdd_pest_check(app)
    print("[✅] Weather and GDD Pest alert task completed.\n")

if __name__ == '__main__':
    # Exécution immédiate pour test
    print("[⏳] Immediate execution of pest alert task.")
    run_gdd_pest_check(app)
    print("[✅] Immediate execution completed.\n")

    try:
        print("[🚀] Scheduler started for pest alerting.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[🛑] Scheduler stopped.")
