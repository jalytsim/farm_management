# Farm Management System

This project is a Flask-based web application for managing farms, creating QR codes, and visualizing data on maps. It includes authentication, QR code generation, and dynamic data visualization.

## Project Structure

```plaintext
farm_management/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── farm.py
│   │   ├── qr.py
│   │   ├── map.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── home.html
│   │   ├── codeQr.html
│   │   ├── index.html
│   │   ├── dynamic.html
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── qr_generator.py
│   │   ├── map_utils.py
├── config.py
├── run.py
├── requirements.txt
├── .env
└── README.md
```

## Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/jalytsim/farm_management.git
   cd farm_management
   ```
2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv please use python 3.12
   source venv/bin/activate  # 
   Windows use `venv\Scripts\activate`
   ```
3. Install the required packages:

   ```sh
   pip install -r requirements.txt please use python 3.12
   ```
4. Set up the environment variables in a `.env` file:

   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=mysql://username:password@localhost/qrcode
   ```
5. Run the application:

   ```sh
   python run.py
   ```

## Features

- User Authentication
- Farm Management
- QR Code Generation
- Data Visualization on Maps

## Déploiement en production

### Architecture (serveur `188.166.125.28`)

| Élément                                | Emplacement                                                                                                |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Backend Flask                            | `/root/farm_management` (dépôt git, venv Python 3.12 dans `venv/`)                                   |
| Service                                  | `farm-management` (systemd), gunicorn sur `127.0.0.1:5002`                                             |
| Frontend (dépôt`zelia-baki/Weather`) | build statique dans`/var/www/nkusu-farm`                                                                 |
| Nginx                                    | `/etc/nginx/sites-available/nkusu-farm` (`nkusu.com`, `www.nkusu.com`, `api.nkusu.com`)            |
| Base de données                         | MySQL 8, base`qrcode`, utilisateur `brian` (mot de passe dans le `.env` du serveur)                  |
| Fichiers utilisateurs                    | `uploads/`, `media/`, `static/uploads/`, `blog_content/` dans `/root/farm_management` (hors git) |

Le frontend appelle l'API en relatif (`/api/...`) : Nginx sert le frontend et proxifie `/api/` vers Flask.
Le serveur est **partagé** avec d'autres applis (`maps` sur :5000, `qrcode` sur :5001, `app.agriyields.com`, ...) : ne jamais toucher à leurs services ni à leurs sites Nginx, et ne pas utiliser ces ports.
`appGlite.service` (racine du dépôt) est l'ancien service de l'ancien serveur (port 5000) : il n'est plus utilisé.

### Mettre à jour le backend

```sh
git push origin main            # depuis le PC
ssh root@188.166.125.28
cd /root/farm_management
git pull origin main
# Seulement si requirements.txt a changé (voir "Dépendances et pièges connus") :
# iconv -f UTF-16 -t UTF-8 requirements.txt | tr -d '\r' > /tmp/req_utf8.txt
# ~/.local/bin/uv pip install --python venv/bin/python -r /tmp/req_utf8.txt
# ~/.local/bin/uv pip uninstall --python venv/bin/python jwt PyJWT && ~/.local/bin/uv pip install --python venv/bin/python "PyJWT==2.8.0" "Flask-JWT-Extended==4.7.1"
systemctl restart farm-management
systemctl status farm-management --no-pager
journalctl -u farm-management -n 50 --no-pager                   # logs
```

Le `.env` n'est pas dans git : il vit uniquement sur le serveur (`/root/farm_management/.env`, `chmod 600`).

### Mettre à jour le frontend

Le build se fait en local (le serveur n'a pas Node) :

```sh
cd Weather                       # dépôt du frontend
git pull && yarn install && yarn build
tar -C dist -cf - . | ssh root@188.166.125.28 'tar -C /var/www/nkusu-farm -xf -'
```

Les fichiers de `dist/assets/` ont un nom haché : les anciens restent sans gêner. Pas de reload Nginx nécessaire pour des fichiers statiques.
`VITE_MAPBOX_TOKEN` doit être présent dans le `.env` du frontend au moment du `yarn build`.

### Installer un nouveau serveur (Ubuntu)

```sh
# 1. Paquets système + Python 3.12 isolé (uv), sans toucher au Python du système
apt-get install -y --no-install-recommends build-essential pkg-config libmysqlclient-dev libffi-dev \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b python3-pip
python3 -m pip install --user uv && export PATH=$HOME/.local/bin:$PATH

# 2. Code + dépendances
cd /root && git clone https://github.com/jalytsim/farm_management.git && cd farm_management
uv venv --python 3.12 venv
iconv -f UTF-16 -t UTF-8 requirements.txt | tr -d '\r' > /tmp/req_utf8.txt   # requirements.txt est en UTF-16
uv pip install --python venv/bin/python -r /tmp/req_utf8.txt
uv pip uninstall --python venv/bin/python jwt PyJWT && uv pip install --python venv/bin/python "PyJWT==2.8.0" "Flask-JWT-Extended==4.7.1"   # versions à garder (voir "pièges connus")

# 3. Base de données (voir aussi "Migrer la base")
PW="Fm-$(openssl rand -hex 14)-Zq9!"     # la politique de mot de passe MySQL exige un mot de passe fort
mysql -e "CREATE DATABASE qrcode CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
          CREATE USER 'brian'@'localhost' IDENTIFIED BY '$PW';
          GRANT ALL PRIVILEGES ON qrcode.* TO 'brian'@'localhost'; FLUSH PRIVILEGES;"

# 4. .env : copier celui du PC (scp), puis mettre le mot de passe ci-dessus dans MYSQL_PASSWORD et MYSQL_HOST=localhost
chmod 600 /root/farm_management/.env

# 5. Dossiers de données
mkdir -p uploads/geojsons media static/uploads blog_content/covers
```

Service systemd (`/etc/systemd/system/farm-management.service`) :

```ini
[Unit]
Description=farm_management Flask API (gunicorn)
After=network.target mysql.service

[Service]
User=root
WorkingDirectory=/root/farm_management
ExecStart=/root/farm_management/venv/bin/gunicorn -c gunicorn_config.py -w 3 -b 127.0.0.1:5002 run:app
Restart=on-failure
RestartSec=5
SuccessExitStatus=143
TimeoutStopSec=15

[Install]
WantedBy=multi-user.target
```

```sh
systemctl daemon-reload && systemctl enable --now farm-management
curl -s http://127.0.0.1:5002/api/crop/count/total      # doit répondre du JSON
```

Site Nginx (`/etc/nginx/sites-available/nkusu-farm`, puis `ln -s` vers `sites-enabled/`) :

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name nkusu.com www.nkusu.com;

    root /var/www/nkusu-farm;
    index index.html;
    client_max_body_size 50M;

    location /api/ {
        proxy_pass http://127.0.0.1:5002;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 180s;
    }
    location /assets/ { expires 1y; add_header Cache-Control "public, immutable"; try_files $uri =404; }
    location / { add_header Cache-Control "no-cache"; try_files $uri /index.html; }
}

server {                                   # API seule
    listen 80;
    listen [::]:80;
    server_name api.nkusu.com;
    client_max_body_size 50M;
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 180s;
    }
}
```

```sh
nginx -t && systemctl reload nginx
# Une fois le DNS (A de nkusu.com, www, api) pointé vers ce serveur :
certbot --nginx -d nkusu.com -d www.nkusu.com -d api.nkusu.com
```

### Migrer la base (ancien serveur MariaDB -> MySQL 8)

```sh
# Sur l'ancien serveur
mysqldump --single-transaction --routines --triggers qrcode | gzip > /root/qrcode_dump.sql.gz
scp /root/qrcode_dump.sql.gz root@188.166.125.28:/root/     # ou via le PC (scp dans les deux sens)

# Sur le nouveau serveur
systemctl stop farm-management
mysql -e "DROP DATABASE IF EXISTS qrcode; CREATE DATABASE qrcode CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
# (les droits de l'utilisateur brian sur qrcode.* sont conservés)
# Le sed retire la ligne d'en-tête MariaDB "/*!999999\- enable the sandbox mode */" que MySQL 8 refuse
gunzip -c /root/qrcode_dump.sql.gz | sed '/^\/\*M\?!999999/d' | mysql qrcode

# Créer les tables des modèles absentes du dump (ajout seulement, ne modifie pas les tables existantes)
cd /root/farm_management && venv/bin/python -c "
from app import create_app
from app.models import db
app = create_app()
with app.app_context():
    db.create_all()
"
systemctl start farm-management
```

### Migrer les fichiers (`uploads/`, `media/`, `static/uploads/`, `blog_content/`)

Ces dossiers ne sont pas dans git (`blog_content/` seulement en partie) : les copier depuis l'ancien serveur.

```sh
# Depuis l'ancien serveur, si celui-ci peut se connecter en SSH au nouveau
cd /root/farm_management
rsync -avz --partial uploads media blog_content root@188.166.125.28:/root/farm_management/
rsync -avz --partial static/uploads root@188.166.125.28:/root/farm_management/static/

# Sinon, en passant par le PC
scp -r root@www.nkusu.com:/root/farm_management/{uploads,media,blog_content} ./old_data/
scp -r ./old_data/* root@188.166.125.28:/root/farm_management/
```

Si `MEDIA_ROOT` est défini dans le `.env` de l'ancien serveur, copier ce dossier-là vers `/root/farm_management/media`.
Les médias sont servis par Flask (`/api/ecommerce/media/<clé>`), pas par Nginx.

### Dépendances et pièges connus

- `requirements.txt` est encodé en **UTF-16** et non épinglé : le convertir avec `iconv` avant `pip`/`uv pip install`.
- Il liste `jwt` **et** `PyJWT`, qui s'écrasent mutuellement (`ImportError: cannot import name 'DecodeError' from 'jwt'`) : garder uniquement `PyJWT`.
- **Versions JWT à figer : `PyJWT==2.8.0` + `Flask-JWT-Extended==4.7.1`** (celles du poste de dev). Avec un PyJWT ≥ 2.10, toutes les routes protégées répondent `422 Subject must be a string`, car `api_login` (`app/routes/auth.py`) met un dictionnaire dans `identity`, donc dans le champ `sub` du token. `Flask-JWT-Extended` 4.7.4 exige lui un PyJWT récent et empêche alors l'appli de démarrer : les deux vont ensemble. Changer cela demande de passer l'identité en chaîne (par exemple l'id utilisateur) dans le backend et dans le frontend.
- Après un changement de serveur ou de `JWT_SECRET_KEY`, les anciens tokens du navigateur sont invalides (`422`) : se déconnecter, puis se reconnecter.
- MySQL du serveur impose une politique de mot de passe forte : ne pas la modifier, elle est partagée avec les autres applis.
- Avant tout `systemctl reload nginx`, lancer `nginx -t`. Si un site voisin référence un certificat Let's Encrypt manquant, le test échoue et le reload est refusé (Nginx continue avec l'ancienne config).
- Le scheduler (alertes météo/parasites) n'est lancé que par un seul worker grâce au fichier verrou `farm_scheduler.lock` du dossier temporaire.

## License

This project is licensed under the Agriyeilds License. See the [LICENSE](LICENSE) file for details.
