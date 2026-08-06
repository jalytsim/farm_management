# app/utils/storage.py
# =============================================================================
#  Stockage des fichiers — abstraction volontairement minimale.
#
#  Le code métier ne sait jamais OÙ le fichier est rangé. Il demande une clé,
#  il demande une URL. Passer du disque local à S3 se fait alors en changeant
#  une variable d'environnement, sans toucher à ecommerce.py ni à la base.
#
#  C'est ce qui manquait dans la première version : l'URL absolue était écrite
#  en dur dans la table. Le jour où le domaine change, ou où tu passes à deux
#  instances derrière un load balancer, toutes les images cassent d'un coup.
#
#  Ce qu'on stocke en base : la CLÉ ("products/ab12cd.jpg").
#  Ce qu'on sert au navigateur : une URL construite à la volée.
# =============================================================================

import os
import uuid
import mimetypes
from abc import ABC, abstractmethod

from flask import current_app, url_for


class StorageBackend(ABC):
    """Contrat commun. Trois opérations suffisent."""

    @abstractmethod
    def save(self, file_storage, key):
        """Écrit le fichier et retourne la clé."""

    @abstractmethod
    def url(self, key):
        """URL publique du fichier."""

    @abstractmethod
    def delete(self, key):
        """Supprime. Ne lève pas si le fichier est déjà absent."""


# ── Disque local ─────────────────────────────────────────────────────────────

class LocalStorage(StorageBackend):
    """Fichiers sur disque, servis par Flask.

    Convient pour une instance unique. Le dossier DOIT être hors du code
    applicatif : un dossier dans app/static/ est effacé à chaque déploiement.
    """

    def __init__(self, root):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def _path(self, key):
        # Empêche toute remontée de chemin : la clé résolue doit rester
        # strictement sous la racine.
        full = os.path.abspath(os.path.join(self.root, key))
        if not full.startswith(os.path.abspath(self.root) + os.sep):
            raise ValueError("Invalid storage key")
        return full

    def save(self, file_storage, key):
        path = self._path(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        file_storage.save(path)
        return key

    def url(self, key):
        return url_for('ecommerce.serve_media', key=key, _external=False)

    def delete(self, key):
        try:
            os.remove(self._path(key))
        except (FileNotFoundError, ValueError):
            pass


# ── S3 / Spaces / R2 ─────────────────────────────────────────────────────────

class S3Storage(StorageBackend):
    """Compatible S3, DigitalOcean Spaces, Cloudflare R2, Backblaze B2 —
    tous exposent la même API.

    Deux modes d'URL :
      - CDN public (S3_PUBLIC_BASE_URL défini) : URL directe, cache navigateur,
        aucun appel serveur. C'est ce que tu veux pour des images produit.
      - Sinon : URL signée temporaire, pour un bucket privé.
    """

    def __init__(self, bucket, region=None, endpoint_url=None,
                 public_base_url=None, signed_url_ttl=3600):
        import boto3  # import tardif : boto3 n'est requis que si ce backend sert
        self.bucket = bucket
        self.public_base_url = (public_base_url or '').rstrip('/')
        self.signed_url_ttl = signed_url_ttl
        self.client = boto3.client(
            's3', region_name=region, endpoint_url=endpoint_url,
            aws_access_key_id=os.environ.get('S3_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('S3_SECRET_KEY'),
        )

    def save(self, file_storage, key):
        content_type = (file_storage.content_type
                        or mimetypes.guess_type(key)[0]
                        or 'application/octet-stream')
        extra = {
            'ContentType': content_type,
            # Une image produit ne change jamais : son nom contient un uuid.
            'CacheControl': 'public, max-age=31536000, immutable',
        }
        if self.public_base_url:
            extra['ACL'] = 'public-read'
        file_storage.seek(0)
        self.client.upload_fileobj(file_storage, self.bucket, key, ExtraArgs=extra)
        return key

    def url(self, key):
        if self.public_base_url:
            return f"{self.public_base_url}/{key}"
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=self.signed_url_ttl,
        )

    def delete(self, key):
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except Exception:
            pass


# ── Sélection du backend ─────────────────────────────────────────────────────

_backend = None


def get_storage():
    """Instancié une fois par process, d'après la configuration."""
    global _backend
    if _backend is not None:
        return _backend

    kind = (current_app.config.get('STORAGE_BACKEND') or 'local').lower()

    if kind == 's3':
        _backend = S3Storage(
            bucket=current_app.config['S3_BUCKET'],
            region=current_app.config.get('S3_REGION'),
            endpoint_url=current_app.config.get('S3_ENDPOINT_URL'),
            public_base_url=current_app.config.get('S3_PUBLIC_BASE_URL'),
        )
    else:
        _backend = LocalStorage(current_app.config['MEDIA_ROOT'])

    return _backend


def build_key(original_filename, prefix='products'):
    """Clé unique et sans surprise.

    Le nom d'origine est jeté : il peut contenir des accents, des espaces, des
    caractères qui cassent une URL S3, ou révéler un chemin interne. Seule
    l'extension est conservée, pour que le Content-Type soit correct.
    """
    ext = ''
    if '.' in original_filename:
        ext = '.' + original_filename.rsplit('.', 1)[1].lower()
    return f"{prefix}/{uuid.uuid4().hex}{ext}"