"""
crop_classifier_utils.py — Classification du type de culture via RandomForest
entraîné à la volée sur les indices Sentinel-2 déjà en cache (SentinelCache).
100% local, aucune dépendance IA tierce.
"""
import logging
import numpy as np

logger = logging.getLogger(__name__)

BASE_INDICES = ['ndvi', 'evi', 'savi', 'ndmi', 'ndwi', 'nmdi', 'nbr', 'bsi']
SEASONAL_INDICES = ['ndvi', 'evi', 'ndmi']  # pour la signature saisonnière (4 trimestres)

# Modèle gardé en mémoire (retrain via endpoint /crop-model/train)
_MODEL_CACHE = {
    'model': None, 'label_encoder': None, 'feature_names': None,
    'trained_at': None, 'metrics': None,
}


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
    """Culture majoritaire d'une ferme (via FarmData.crop_id -> Crop.name)."""
    from app.models import FarmData, Crop
    from collections import Counter

    rows = FarmData.query.filter_by(farm_id=farm_id).filter(FarmData.crop_id.isnot(None)).all()
    if not rows:
        return None
    counts = Counter(r.crop_id for r in rows)
    top_crop_id = counts.most_common(1)[0][0]
    crop = Crop.query.get(top_crop_id)
    return crop.name if crop else None


def build_training_dataset(fetch_missing=False, max_fetch=15):
    """
    Construit (X, y, farm_ids) à partir des fermes ayant un crop_id assigné
    et un historique Sentinel exploitable (cache existant, ou fetch limité).
    """
    from app.models import Farm, FarmData, SentinelCache
    from app.utils.sentinel_utils import get_sat_index_full

    farm_ids_with_crop = (
        Farm.query.join(FarmData, Farm.farm_id == FarmData.farm_id)
        .filter(FarmData.crop_id.isnot(None))
        .with_entities(Farm.farm_id).distinct().all()
    )
    farm_ids_with_crop = [f[0] for f in farm_ids_with_crop]

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
            result, error = get_sat_index_full('farm', farm_id)
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
    logger.info(f'[CropClassifier] Trained: {metrics["n_samples"]} samples, '
                f'{metrics["n_classes"]} classes, OOB={metrics["oob_score"]}')
    return metrics, None


def get_model_status():
    if _MODEL_CACHE['model'] is None:
        return {'trained': False}
    return {
        'trained':     True,
        'trained_at':  _MODEL_CACHE['trained_at'],
        'metrics':     _MODEL_CACHE['metrics'],
    }


def predict_crop(entity_type, entity_id):
    """Prédit la culture d'une ferme à partir de son historique Sentinel actuel."""
    from app.utils.sentinel_utils import get_sat_index_full

    if _MODEL_CACHE['model'] is None:
        return None, 'Model not trained yet — call /api/sentinel/crop-model/train first'

    result, error = get_sat_index_full(entity_type, entity_id)
    if error:
        return None, error

    feats = extract_features(result.get('history'))
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

    return {
        'entity_id':        entity_id,
        'predicted_crop':   top[0]['crop'] if top else None,
        'confidence':       top[0]['confidence'] if top else None,
        'top_predictions':  top,
        'model_trained_at': _MODEL_CACHE['trained_at'],
    }, None