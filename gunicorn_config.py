# gunicorn_config.py

# ✅ Le défaut Gunicorn (30s) est trop court pour l'API ISRIC SoilGrids
# (_fetch_soc_soilgrids, sentinel_utils.py) qui répond régulièrement en 25-30s
# — le worker était tué/redémarré avant même que notre propre timeout interne
# (45s) ne se déclenche, ce qui faisait échouer le SOC en production.
timeout = 90

# ❌ Supprime ceci
# def on_starting(server):
#     from app import create_app
#     from app.__init__ import start_scheduler
#     app = create_app()
#     start_scheduler(app)
#     server.log.info("✅ Scheduler démarré via on_starting (Gunicorn master process)")
