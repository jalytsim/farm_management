"""
hscode_sync.py
──────────────────────────────────────────────────────────────────────────────
Rend la liste des codes HS du formulaire DDS dynamique et fiable :

1. Pour chaque code de l'Annexe I (table hscode), crée ses sous-positions à
   6 chiffres d'après la nomenclature du Système harmonisé
   (app/data/hs_nomenclature.csv) dans hscode_subheading.
2. Demande à TRACES si le code lui-même et chaque sous-position sont acceptés
   (EUDRClient.check_hs_code, qui ne crée jamais de DDS) et enregistre le verdict.

Le formulaire ne propose ensuite que les codes acceptés, et /api/eudr/submit
refuse d'avance un code que TRACES a déjà rejeté.

Lancement : POST /api/hscode/sync-traces (admin), automatiquement à la
création/modification d'un code HS, ou en ligne de commande :
    python -c "from app import create_app; from app.utils.hscode_sync import sync_all; \
               app = create_app(); app.app_context().push(); print(sync_all())"
"""

import csv
import os
import threading
import time
from datetime import datetime

NOMENCLATURE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'hs_nomenclature.csv')
PROBE_DELAY_S = 0.5   # ménage le serveur TRACES

_nomenclature = None
_state_lock = threading.Lock()
_state = {'running': False, 'done': 0, 'total': 0, 'started_at': None, 'finished_at': None, 'error': None}


def load_nomenclature():
    """{code6: description} — chargé une fois."""
    global _nomenclature
    if _nomenclature is None:
        with open(NOMENCLATURE_PATH, encoding='utf-8') as f:
            _nomenclature = {r['code']: r['description'] for r in csv.DictReader(f)}
    return _nomenclature


def subheadings_for(digits):
    """Sous-positions à 6 chiffres sous un code de 2 à 6 chiffres."""
    nomenclature = load_nomenclature()
    if len(digits) >= 6:
        return {digits[:6]: nomenclature.get(digits[:6])}
    return {code: desc for code, desc in nomenclature.items() if code.startswith(digits)}


def populate_subheadings(hscode):
    """Crée les sous-positions manquantes d'un HSCode (sans interroger TRACES)."""
    from app.models import HSCodeSubheading, db
    existing = {s.code for s in hscode.subheadings}
    wanted = subheadings_for(hscode.digits)
    for code, desc in wanted.items():
        if code not in existing:
            db.session.add(HSCodeSubheading(hscode_id=hscode.id, code=code, description=desc))
    # Sous-positions qui ne correspondent plus au code (code HS modifié) ; la
    # position parente à 4 chiffres (repli, cf. check_hscode) est conservée.
    for sub in list(hscode.subheadings):
        if sub.code not in wanted and sub.code != _parent_heading(hscode.digits):
            db.session.delete(sub)
    db.session.commit()


def _parent_heading(digits):
    return digits[:4] if len(digits) > 4 else None


def _client():
    from app.routes.api_eudr import eudr_client
    return eudr_client


def check_hscode(hscode, client=None, recheck=False, progress=None):
    """Vérifie un HSCode et ses sous-positions auprès de TRACES."""
    from app.models import db
    client = client or _client()
    populate_subheadings(hscode)
    now = datetime.utcnow
    if recheck or hscode.traces_valid is None:
        hscode.traces_valid = client.check_hs_code(hscode.digits)
        hscode.traces_checked_at = now()
        db.session.commit()
        time.sleep(PROBE_DELAY_S)
        if progress:
            progress()
    # Repli : TRACES refuse certains codes à 6 chiffres de l'Annexe I mais accepte
    # leur position à 4 chiffres (vérifié : 010221 refusé, 0102 accepté). On la
    # propose alors comme code déclarable.
    parent = _parent_heading(hscode.digits)
    if hscode.traces_valid is False and parent:
        from app.models import HSCodeSubheading
        sub = next((x for x in hscode.subheadings if x.code == parent), None)
        if sub is None:
            sub = HSCodeSubheading(hscode_id=hscode.id, code=parent,
                                   description=f'Heading {parent} (code accepted by TRACES)')
            db.session.add(sub)
            db.session.commit()
    for sub in hscode.subheadings:
        if sub.code == hscode.digits:
            sub.traces_valid = hscode.traces_valid   # même code, déjà vérifié
            sub.traces_checked_at = hscode.traces_checked_at
        elif recheck or sub.traces_valid is None:
            sub.traces_valid = client.check_hs_code(sub.code)
            sub.traces_checked_at = now()
            time.sleep(PROBE_DELAY_S)
        db.session.commit()
        if progress:
            progress()


def sync_all(hscode_ids=None, recheck=False):
    """Synchronise tous les codes (ou ceux listés). Retourne un résumé."""
    from app.models import HSCode
    query = HSCode.query
    if hscode_ids:
        query = query.filter(HSCode.id.in_(hscode_ids))
    codes = query.order_by(HSCode.code).all()
    for h in codes:
        populate_subheadings(h)

    def _todo(h):
        n = 1 if (recheck or h.traces_valid is None) else 0
        return n + sum(1 for s in h.subheadings
                       if s.code != h.digits and (recheck or s.traces_valid is None))

    with _state_lock:
        _state.update(total=sum(_todo(h) for h in codes), done=0)

    def _progress():
        with _state_lock:
            _state['done'] += 1

    client = _client()
    for h in codes:
        check_hscode(h, client=client, recheck=recheck, progress=_progress)
    return summary()


def summary():
    from app.models import HSCode, HSCodeSubheading
    subs = HSCodeSubheading.query.all()
    return {
        'hscodes': HSCode.query.count(),
        'hscodes_valid': HSCode.query.filter_by(traces_valid=True).count(),
        'hscodes_invalid': HSCode.query.filter_by(traces_valid=False).count(),
        'subheadings': len(subs),
        'subheadings_valid': sum(1 for s in subs if s.traces_valid is True),
        'subheadings_invalid': sum(1 for s in subs if s.traces_valid is False),
        'subheadings_unchecked': sum(1 for s in subs if s.traces_valid is None),
    }


def start_background_sync(app, hscode_ids=None, recheck=False):
    """Lance sync_all dans un thread (plusieurs minutes pour toute la table)."""
    with _state_lock:
        if _state['running']:
            return False
        _state.update(running=True, started_at=datetime.utcnow().isoformat(), finished_at=None, error=None)

    def _run():
        try:
            with app.app_context():
                sync_all(hscode_ids=hscode_ids, recheck=recheck)
        except Exception as e:   # noqa: BLE001 — rapporté via sync_status()
            with _state_lock:
                _state['error'] = str(e)
        finally:
            with _state_lock:
                _state.update(running=False, finished_at=datetime.utcnow().isoformat())

    threading.Thread(target=_run, daemon=True).start()
    return True


def sync_status():
    with _state_lock:
        return dict(_state)


def lookup_hs_status(digits):
    """
    Verdict TRACES connu pour un code saisi : True / False / None (inconnu).
    Utilisé par /api/eudr/submit pour refuser d'avance un code déjà rejeté.
    """
    from app.models import HSCode, HSCodeSubheading
    verdicts = [s.traces_valid for s in HSCodeSubheading.query.filter_by(code=digits).all()]
    verdicts += [h.traces_valid for h in HSCode.query.all() if h.digits == digits]
    known = [v for v in verdicts if v is not None]
    if not known:
        return None
    return any(known)
