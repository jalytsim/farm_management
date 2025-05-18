from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from tasks import daily_pest_check
import time

scheduler = BackgroundScheduler(timezone="UTC")

def start_scheduler():
    print("🔁 Démarrage du scheduler toutes les minutes (test)...")
    
    # Supprime le job existant s'il existe
    if scheduler.get_job('daily_pest_check'):
        scheduler.remove_job('daily_pest_check')

    scheduler.add_job(
        daily_pest_check,
        trigger=CronTrigger(minute='*'),  # ⏱️ Chaque minute
        id='daily_pest_check',
        replace_existing=True
    )

    scheduler.start()
