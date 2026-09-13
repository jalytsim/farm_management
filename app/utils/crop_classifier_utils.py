"""
crop_classifier_utils.py — Classification du type de culture via RandomForest
entraîné à la volée sur les indices Sentinel-2 déjà en cache (SentinelCache).
100% local, aucune dépendance IA tierce.
"""
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)

BASE_INDICES = ['ndvi', 'evi', 'savi', 'ndmi', 'ndwi', 'nmdi', 'nbr', 'bsi']
SEASONAL_INDICES = ['ndvi', 'evi', 'ndmi']  # pour la signature saisonnière (4 trimestres)

# ✅ FIX : le modèle n'était gardé QU'EN MÉMOIRE (_MODEL_CACHE ci-dessous), donc
# perdu à chaque redémarrage du process, ET invisible des autres workers Gunicorn
# (chacun a sa propre mémoire) — symptôme typique : "not trained" de façon
# intermittente selon le worker qui répond, malgré un entraînement récent.
# On persiste maintenant le modèle sur disque et on le recharge paresseusement.
_MODEL_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml_models')
_MODEL_PATH = os.path.join(_MODEL_DIR, 'crop_classifier.joblib')

# Modèle gardé en mémoire PAR PROCESS — voir _load_model_from_disk() pour le
# fallback disque partagé entre tous les workers/redémarrages.
_MODEL_CACHE = {
    'model': None, 'label_encoder': None, 'feature_names': None,
    'trained_at': None, 'metrics': None,
}


def _save_model_to_disk():
    import joblib
    os.makedirs(_MODEL_DIR, exist_ok=True)
    joblib.dump({
        'model':         _MODEL_CACHE['model'],
        'label_encoder': _MODEL_CACHE['label_encoder'],
        'feature_names': _MODEL_CACHE['feature_names'],
        'trained_at':    _MODEL_CACHE['trained_at'],
        'metrics':       _MODEL_CACHE['metrics'],
    }, _MODEL_PATH)


def _load_model_from_disk():
    """Charge le modèle depuis le disque dans le cache mémoire de CE process,
    si un modèle entraîné existe et n'est pas déjà chargé ici."""
    if _MODEL_CACHE['model'] is not None:
        return True
    if not os.path.exists(_MODEL_PATH):
        return False
    import joblib
    try:
        saved = joblib.load(_MODEL_PATH)
        _MODEL_CACHE.update(saved)
        logger.info(f'[CropClassifier] Model loaded from disk (trained_at={saved.get("trained_at")})')
        return True
    except Exception as e:
        logger.error(f'[CropClassifier] Failed to load model from disk: {e}')
        return False


def _val(row, idx):
    v = row.get(idx)
    return v.get('value') if isinstance(v, dict) else v


def extract_features(history_out):
    """
    Transforme un historique {date, ndvi:{value,...}, evi:{...}, ...} en un
    vecteur de features numériques (signature spectrale + saisonnière).
    Retourne None si pas assez de données exploitables.
    """
    if not history_out:
        return None

    features = {}
    usable_points = 0

    for idx in BASE_INDICES:
        vals = [v for v in (_val(r, idx) for r in history_out) if v is not None]
        if vals:
            usable_points = max(usable_points, len(vals))
            features[f'{idx}_mean'] = float(np.mean(vals))
            features[f'{idx}_std']  = float(np.std(vals))
            features[f'{idx}_min']  = float(np.min(vals))
            features[f'{idx}_max']  = float(np.max(vals))
        else:
            features[f'{idx}_mean'] = features[f'{idx}_std'] = 0.0
            features[f'{idx}_min']  = features[f'{idx}_max']  = 0.0

    # Signature saisonnière : moyenne par trimestre calendaire (Q1..Q4)
    for idx in SEASONAL_INDICES:
        quarter_vals = {1: [], 2: [], 3: [], 4: []}
        for r in history_out:
            v = _val(r, idx)
            if v is None:
                continue
            month = int(r['date'][5:7])
            q = (month - 1) // 3 + 1
            quarter_vals[q].append(v)
        for q in range(1, 5):
            vv = quarter_vals[q]
            features[f'{idx}_q{q}'] = float(np.mean(vv)) if vv else 0.0

    if usable_points < 4:
        return None
    return features


def _get_farm_crop_label(farm_id):
    """
    Culture d'une ferme, pour l'entraînement : priorité à FarmData (culture
    majoritaire réellement enregistrée) ; à défaut, retombe sur une prédiction
    confirmée manuellement dans le dashboard (CropPredictionConfirmation) —
    c'est ce qui permet à une ferme sans donnée agronomique connue d'entrer
    dans la banque d'entraînement une fois sa culture confirmée à l'écran.
    """
    from app.models import FarmData, Crop, CropPredictionConfirmation
    from collections import Counter

    rows = FarmData.query.filter_by(farm_id=farm_id).filter(FarmData.crop_id.isnot(None)).all()
    if rows:
        counts = Counter(r.crop_id for r in rows)
        top_crop_id = counts.most_common(1)[0][0]
        crop = Crop.query.get(top_crop_id)
        if crop:
            return crop.name

    confirmation = CropPredictionConfirmation.query.filter_by(farm_id=farm_id).first()
    if confirmation:
        crop = Crop.query.get(confirmation.crop_id)
        if crop:
            return crop.name

    return None


def confirm_crop_prediction(farm_id, crop_id, confirmed_by=None, predicted_crop=None, confidence=None):
    """
    Enregistre la confirmation humaine d'une culture prédite pour `farm_id`
    (voir bouton "Confirmer" dans CropPredictionPanel.jsx). Une ferme n'a
    qu'une confirmation active à la fois (upsert) ; le prochain
    /crop-model/train récupérera automatiquement cette ferme via
    _get_farm_crop_label() ci-dessus, sans toucher à FarmData.
    """
    from app import db
    from app.models import Farm, Crop, CropPredictionConfirmation

    if not Farm.query.filter_by(farm_id=farm_id).first():
        return None, 'Farm not found'
    if not Crop.query.get(crop_id):
        return None, 'Crop not found'

    entry = CropPredictionConfirmation.query.filter_by(farm_id=farm_id).first()
    if entry is None:
        entry = CropPredictionConfirmation(farm_id=farm_id)
        db.session.add(entry)

    from datetime import datetime
    entry.crop_id        = crop_id
    entry.predicted_crop = predicted_crop
    entry.confidence     = confidence
    entry.confirmed_by   = confirmed_by
    entry.confirmed_at   = datetime.utcnow()
    db.session.commit()

    return entry, None


def build_training_dataset(fetch_missing=False, max_fetch=15):
    """
    Construit (X, y, farm_ids) à partir des fermes ayant un crop_id assigné
    (FarmData) ou une prédiction confirmée (CropPredictionConfirmation), avec
    un historique Sentinel exploitable (cache existant, ou fetch limité).
    """
    from app.models import Farm, FarmData, CropPredictionConfirmation, SentinelCache
    from app.utils.sentinel_utils import get_sat_index_full

    farm_ids_with_crop = (
        Farm.query.join(FarmData, Farm.farm_id == FarmData.farm_id)
        .filter(FarmData.crop_id.isnot(None))
        .with_entities(Farm.farm_id).distinct().all()
    )
    confirmed_farm_ids = CropPredictionConfirmation.query.with_entities(
        CropPredictionConfirmation.farm_id
    ).distinct().all()
    farm_ids_with_crop = sorted({f[0] for f in farm_ids_with_crop} | {f[0] for f in confirmed_farm_ids})

    X, y, used_farm_ids = [], [], []
    fetched = 0

    for farm_id in farm_ids_with_crop:
        label = _get_farm_crop_label(farm_id)
        if not label:
            continue

        cache = SentinelCache.query.filter_by(farm_id=farm_id).first()
        history_out = None
        if cache:
            history_out = cache.get_history()
        elif fetch_missing and fetched < max_fetch:
            # ✅ FIX : get_sat_index_full est `async def` — l'appeler directement
            # renvoie une coroutine jamais exécutée (TypeError au unpacking).
            import asyncio
            result, error = asyncio.run(get_sat_index_full('farm', farm_id))
            fetched += 1
            if result:
                history_out = result.get('history')

        if not history_out:
            continue

        feats = extract_features(history_out)
        if feats is None:
            continue

        X.append(feats)
        y.append(label)
        used_farm_ids.append(farm_id)

    return X, y, used_farm_ids


def train_model(fetch_missing=False, max_fetch=15):
    """Entraîne (ou ré-entraîne) le RandomForest en mémoire."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    from datetime import datetime

    X_dicts, y_labels, farm_ids = build_training_dataset(fetch_missing, max_fetch)

    n_classes = len(set(y_labels))
    if len(X_dicts) < 5 or n_classes < 2:
        return None, (
            f'Pas assez de données pour entraîner : {len(X_dicts)} fermes exploitables, '
            f'{n_classes} culture(s) distincte(s). Il faut au moins 5 fermes et 2 cultures différentes '
            f'avec un crop_id assigné et un historique satellite en cache.'
        )

    feature_names = sorted(X_dicts[0].keys())
    X = np.array([[fd[k] for k in feature_names] for fd in X_dicts])

    le = LabelEncoder()
    y = le.fit_transform(y_labels)

    clf = RandomForestClassifier(
        n_estimators=200, max_depth=8, min_samples_leaf=2,
        class_weight='balanced', oob_score=True, random_state=42,
    )
    clf.fit(X, y)

    importances = sorted(
        zip(feature_names, clf.feature_importances_.tolist()),
        key=lambda t: -t[1]
    )[:10]

    metrics = {
        'n_samples':       len(X_dicts),
        'n_classes':       n_classes,
        'classes':         le.classes_.tolist(),
        'oob_score':       round(float(clf.oob_score_), 4) if hasattr(clf, 'oob_score_') else None,
        'top_features':    [{'feature': f, 'importance': round(i, 4)} for f, i in importances],
        'farms_used':      farm_ids,
    }

    _MODEL_CACHE.update({
        'model': clf, 'label_encoder': le, 'feature_names': feature_names,
        'trained_at': datetime.utcnow().isoformat(), 'metrics': metrics,
    })
    _save_model_to_disk()
    logger.info(f'[CropClassifier] Trained: {metrics["n_samples"]} samples, '
                f'{metrics["n_classes"]} classes, OOB={metrics["oob_score"]}')
    return metrics, None


def get_model_status():
    _load_model_from_disk()
    if _MODEL_CACHE['model'] is None:
        return {'trained': False}
    return {
        'trained':     True,
        'trained_at':  _MODEL_CACHE['trained_at'],
        'metrics':     _MODEL_CACHE['metrics'],
    }


def _predict_from_history(history_out):
    """
    Coeur de la prédiction, factorisé pour être partagé entre predict_crop()
    (ferme authentifiée, historique via get_sat_index_full) et
    predict_crop_from_geojson() (guest, historique via get_sat_index_full_guest) —
    évite de dupliquer la logique modèle/feature/top-3.
    """
    _load_model_from_disk()
    if _MODEL_CACHE['model'] is None:
        return None, 'Model not trained yet — call /api/sentinel/crop-model/train first'

    feats = extract_features(history_out)
    if feats is None:
        return None, 'Not enough satellite history to extract a reliable signature'

    feature_names = _MODEL_CACHE['feature_names']
    x = np.array([[feats.get(k, 0.0) for k in feature_names]])

    clf = _MODEL_CACHE['model']
    le  = _MODEL_CACHE['label_encoder']

    proba = clf.predict_proba(x)[0]
    order = np.argsort(proba)[::-1]

    top = [
        {'crop': le.classes_[i], 'confidence': round(float(proba[i]) * 100, 2)}
        for i in order[:3] if proba[i] > 0
    ]

    # id du crop prédit (pour le bouton "Confirmer" côté frontend, qui a
    # besoin d'un crop_id, pas juste du nom affiché) — best-effort, None si
    # le nom prédit ne correspond à aucun Crop existant.
    predicted_crop_id = None
    if top:
        from app.models import Crop
        crop_row = Crop.query.filter_by(name=top[0]['crop']).first()
        predicted_crop_id = crop_row.id if crop_row else None

    return {
        'predicted_crop':     top[0]['crop'] if top else None,
        'predicted_crop_id':  predicted_crop_id,
        'confidence':         top[0]['confidence'] if top else None,
        'top_predictions':    top,
        'model_trained_at':   _MODEL_CACHE['trained_at'],
    }, None


def predict_crop(entity_type, entity_id):
    """Prédit la culture d'une ferme à partir de son historique Sentinel actuel."""
    import asyncio
    from app.utils.sentinel_utils import get_sat_index_full

    # ✅ FIX : get_sat_index_full est `async def` — sans asyncio.run, predict_crop
    # levait TypeError: cannot unpack non-iterable coroutine object à CHAQUE
    # appel, ce qui explique une bonne partie du "ça ne marche pas très bien".
    result, error = asyncio.run(get_sat_index_full(entity_type, entity_id))
    if error:
        return None, error

    partial, error = _predict_from_history(result.get('history'))
    if error:
        return None, error

    return {
        'entity_id':          entity_id,
        **partial,
    }, None


def predict_crop_from_geojson(geojson, guest_phone_number):
    """
    Variante guest de predict_crop() : géométrie fournie directement, pas de
    lookup Farm en DB — réutilisé par le Carbon Report guest (property_type
    'farm') pour afficher aussi la culture prédite, en plus du SOC SoilGrids.
    """
    import asyncio
    from app.utils.sentinel_utils import get_sat_index_full_guest

    result, error = asyncio.run(get_sat_index_full_guest(geojson, guest_phone_number))
    if error:
        return None, error

    return _predict_from_history(result.get('history'))