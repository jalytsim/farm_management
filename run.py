from app import create_app
from app.__init__ import start_scheduler  # ou refactor dans un autre fichier si tu veux

app = create_app()
start_scheduler(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
