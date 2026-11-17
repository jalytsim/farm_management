"""
Données cartographiques compactes des polygones (fermes / forêts) pour les cartes
« View all » et le tableau de bord.

Pourquoi : avec 50 000+ fermes et 1,2 M de points, renvoyer tous les points à
chaque ouverture de carte prenait des minutes et bloquait le navigateur.

  - centroids(scope)   : un point + une surface par entité, calculés en un seul
                         passage SQL brut, mis en cache disque (gzip) partagé par
                         les workers gunicorn.
  - polygons_in_bbox() : contours des seules entités visibles (carte zoomée).

Invalidation : toute écriture ORM sur Point (ajout, modif, suppression, y compris
query.update()/delete()) « touche » un fichier témoin ; un cache plus ancien
que ce témoin est reconstruit. Les insertions hors ORM (script d'import,
SQL brut) sont rattrapées par la durée de vie maximale CACHE_TTL.
"""
import gzip
import json
import math
import os
import tempfile
import threading
import time

from flask import current_app
from sqlalchemy import bindparam, event, text
from sqlalchemy.orm import Session

CACHE_TTL = 6 * 3600                    # secondes
CACHE_DIR = os.path.join(tempfile.gettempdir(), 'nkusu_map_cache')
STAMP = os.path.join(CACHE_DIR, 'points.stamp')
MAX_BBOX_ENTITIES = 4000                # au-delà, la vue est trop large pour des contours
EARTH_R = 6371008.8


# ── Invalidation ─────────────────────────────────────────────────────────────

def bump():
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(STAMP, 'w') as fh:
        fh.write(str(time.time()))


def _stamp_time():
    try:
        return os.path.getmtime(STAMP)
    except OSError:
        return 0.0


def register_invalidation():
    """À appeler une fois au démarrage de l'app."""
    from app.models import Point

    @event.listens_for(Session, 'after_flush')
    def _after_flush(session, _ctx):
        for obj in (*session.new, *session.dirty, *session.deleted):
            if isinstance(obj, Point):
                bump()
                return

    @event.listens_for(Session, 'do_orm_execute')
    def _bulk(state):
        if (state.is_update or state.is_delete or state.is_insert) and any(
                m.class_ is Point for m in state.all_mappers):
            bump()


# ── Calculs ──────────────────────────────────────────────────────────────────

def _ring_area_m2(ring):
    """Aire géodésique approchée (formule de l'aire sphérique, comme turf.area)."""
    n = len(ring)
    if n < 3:
        return 0.0
    total = 0.0
    for i in range(n):
        lon1, lat1 = ring[i]
        lon2, lat2 = ring[(i + 1) % n]
        total += math.radians(lon2 - lon1) * (2 + math.sin(math.radians(lat1)) + math.sin(math.radians(lat2)))
    return abs(total * EARTH_R * EARTH_R / 2.0)


def _scope_sql(user):
    if user.is_admin:
        return '', {}
    return ' AND created_by = :uid', {'uid': user.id}


def _iter_rings(rows):
    """rows triés par owner_id, id → (owner_id, [(lon, lat), …])."""
    current, ring = None, []
    for owner_id, lon, lat in rows:
        if owner_id != current:
            if current is not None:
                yield current, ring
            current, ring = owner_id, []
        ring.append((lon, lat))
    if current is not None:
        yield current, ring


def _open_ring(ring):
    if len(ring) > 1 and ring[0] == ring[-1]:
        return ring[:-1]
    return ring


def _build_centroids(db, owner_type, user):
    scope, params = _scope_sql(user)
    rows = db.session.execute(text(
        'SELECT owner_id, CAST(longitude AS DOUBLE), CAST(latitude AS DOUBLE) FROM point '
        f'WHERE owner_type = :ot AND owner_id IS NOT NULL{scope} ORDER BY owner_id, id'),
        {'ot': owner_type, **params})
    ids, coords, areas = [], [], []
    total = 0.0
    for owner_id, ring in _iter_rings(rows):
        ring = _open_ring(ring)
        n = len(ring)
        lon = sum(p[0] for p in ring) / n
        lat = sum(p[1] for p in ring) / n
        area = _ring_area_m2(ring)
        total += area
        ids.append(owner_id)
        coords.append([round(lon, 6), round(lat, 6)])
        areas.append(round(area, 1))
    return {'owner_type': owner_type, 'count': len(ids), 'total_area_m2': round(total, 1),
            'ids': ids, 'coords': coords, 'areas': areas}


# ── Cache disque ─────────────────────────────────────────────────────────────

def _cache_path(owner_type, user):
    scope = 'all' if user.is_admin else f'u{user.id}'
    return os.path.join(CACHE_DIR, f'centroids_{owner_type}_{scope}.json.gz')


def _rebuild(db, owner_type, user, path):
    data = _build_centroids(db, owner_type, user)
    blob = gzip.compress(json.dumps(data, separators=(',', ':')).encode(), compresslevel=6)
    os.makedirs(CACHE_DIR, exist_ok=True)
    tmp = f'{path}.{os.getpid()}.{threading.get_ident()}.tmp'
    with open(tmp, 'wb') as fh:
        fh.write(blob)
    os.replace(tmp, path)                # écriture atomique : un autre worker peut lire en même temps
    return blob


def _try_lock(path):
    """Un seul rebuild en arrière-plan à la fois (tous workers confondus)."""
    lock = path + '.lock'
    try:
        if time.time() - os.path.getmtime(lock) > 600:       # verrou orphelin
            os.remove(lock)
    except OSError:
        pass
    try:
        os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        return lock
    except FileExistsError:
        return None


def _rebuild_in_background(app, owner_type, user_id, path):
    lock = _try_lock(path)
    if lock is None:
        return

    def run():
        try:
            with app.app_context():
                from app import db
                from app.models import User
                _rebuild(db, owner_type, User.query.get(user_id), path)
        except Exception:                                    # le cache périmé reste servi
            app.logger.exception('map cache rebuild failed')
        finally:
            try:
                os.remove(lock)
            except OSError:
                pass

    threading.Thread(target=run, daemon=True).start()


def centroids_gz(db, owner_type, user):
    """
    Octets gzip du JSON des centroïdes.
      - cache à jour            → servi tel quel
      - cache périmé, admin     → servi tout de suite, reconstruit en arrière-plan
                                  (50 000+ fermes : ~30 s de calcul)
      - cache périmé, autre     → reconstruit tout de suite (quelques secondes), pour
                                  qu'un polygone qu'on vient de dessiner apparaisse
    """
    path = _cache_path(owner_type, user)
    try:
        mtime = os.path.getmtime(path)
        fresh = mtime > _stamp_time() and time.time() - mtime < CACHE_TTL
        if fresh or user.is_admin:
            with open(path, 'rb') as fh:
                blob = fh.read()
            if not fresh:
                _rebuild_in_background(current_app._get_current_object(), owner_type, user.id, path)
            return blob
    except OSError:
        pass
    return _rebuild(db, owner_type, user, path)


def centroids(db, owner_type, user):
    return json.loads(gzip.decompress(centroids_gz(db, owner_type, user)))


def polygons_in_bbox(db, owner_type, user, west, south, east, north, limit=MAX_BBOX_ENTITIES):
    """Contours des entités dont le centre est dans la zone ; None si la zone en contient trop."""
    data = centroids(db, owner_type, user)
    inside = [oid for oid, (lon, lat) in zip(data['ids'], data['coords'])
              if west <= lon <= east and south <= lat <= north]
    if len(inside) > limit:
        return None, len(inside)
    features = []
    query = text('SELECT owner_id, CAST(longitude AS DOUBLE), CAST(latitude AS DOUBLE) FROM point '
                 'WHERE owner_type = :ot AND owner_id IN :ids ORDER BY owner_id, id'
                 ).bindparams(bindparam('ids', expanding=True))
    for start in range(0, len(inside), 1000):
        rows = db.session.execute(query, {'ot': owner_type, 'ids': inside[start:start + 1000]})
        for owner_id, ring in _iter_rings(rows):
            ring = _open_ring(ring)
            if len(ring) < 3:
                continue
            ring = [[round(lon, 6), round(lat, 6)] for lon, lat in ring]
            ring.append(ring[0])
            features.append({'type': 'Feature', 'properties': {'owner_id': owner_id},
                             'geometry': {'type': 'Polygon', 'coordinates': [ring]}})
    return {'type': 'FeatureCollection', 'features': features}, len(inside)
