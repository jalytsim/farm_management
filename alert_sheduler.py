from apscheduler.schedulers.blocking import BlockingScheduler
from app import create_app
from app.utils.scheduler import run_weather_check
from app.utils.schedulerpest import run_gdd_pest_check

app = create_app()
scheduler = BlockingScheduler()

# Tâche planifiée pour la météo (à 6h du matin)
@scheduler.scheduled_job('cron', hour=6, minute=0)
def scheduled_weather_task():
    print("[🕕] Weather alert task started at 6h.")
    run_weather_check(app)
    print("[✅] Weather alert task completed.\n")

# Tâche planifiée pour les ravageurs (à 6h aussi, ou modifie selon ton besoin)
@scheduler.scheduled_job('cron', hour=6, minute=5)  # Exécute 5 minutes après la météo
def scheduled_pest_task():
    print("[🕷️] GDD Pest alert task started at 6:05.")
    run_gdd_pest_check(app)
    print("[✅] GDD Pest alert task completed.\n")

if __name__ == '__main__':
    # Exécution immédiate pour test
    print("[⏳] Immediate execution for testing both alerts.")
    run_weather_check(app)
    run_gdd_pest_check(app)
    print("[✅] Immediate execution of both completed.\n")

    try:
        print("[🚀] Scheduler started. Waiting for the next executions.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("[🛑] Scheduler stopped.")

# 🔁 Planification toutes les 1 minute pour test
# @scheduler.scheduled_job('cron', minute='*/1')
# def scheduled_task():
#     print("[🕕] Weather and GDD Pest alert task started.")
#     run_weather_check(app)
#     run_gdd_pest_check(app)
#     print("[✅] Weather and GDD Pest alert task completed.\n")

# if __name__ == '__main__':
#     # 🔁 Exécution immédiate pour test rapide
#     print("[⏳] Immediate execution of weather and pest alert task.")
#     run_weather_check(app)
#     run_gdd_pest_check(app)
#     print("[✅] Immediate execution completed.\n")

#     try:
#         print("[🚀] Scheduler started. Running every 1 minute for testing.")
#         scheduler.start()
#     except (KeyboardInterrupt, SystemExit):
#         print("[🛑] Scheduler stopped.")