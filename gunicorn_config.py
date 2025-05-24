# gunicorn_config.py

# ❌ Supprime ceci
# def on_starting(server):
#     from app import create_app
#     from app.__init__ import start_scheduler
#     app = create_app()
#     start_scheduler(app)
#     server.log.info("✅ Scheduler démarré via on_starting (Gunicorn master process)")
