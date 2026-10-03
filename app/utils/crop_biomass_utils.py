"""
crop_biomass_utils.py
──────────────────────────────────────────────────────────────────────────────
Biomasse aérienne par culture, à partir des indices Sentinel-2 (cultures
annuelles + cacao) ou d'une équation allométrique (café).

| Culture | Formule                                      | Indice(s)     |
| ------- | -------------------------------------------- | ------------- |
| Maize   | 45.2 + 310.5 × NDVI                          | NDVI          |
| Rice    | 120.3 + 250.7 × EVI                          | EVI           |
| Wheat   | -80 + 400 × NDVI + 180 × SAVI                | NDVI + SAVI   |
| Coffee  | 0.0673 × (ρ × DBH² × H)^0.976  (kg / arbre)  | ρ, DBH, H     |
| Cocoa   | 25 + 280 × NDVI + x × NDII                   | NDVI + NDII   |

Hypothèses (à confirmer / recalibrer localement) :
  - Les régressions indice → biomasse donnent une biomasse sèche en g/m²
    (1 g/m² = 0.01 t/ha). Résultat borné à 0 (pas de biomasse négative quand
    le NDVI est très bas, ex. wheat sur sol nu).
  - NDII = (B08 - B11) / (B08 + B11) : c'est exactement le NDMI déjà calculé
    par l'evalscript Sentinel (sentinel_utils.py), on le réutilise.
  - Café : équation pantropicale de Chave et al. (2014), exposant 0.976.
    ρ = densité du bois (g/cm³), DBH en cm, H en m → AGB en kg par arbre.
  - Cacao : le coefficient x du NDII n'a pas été fourni. COCOA_NDII_COEF vaut 0
    tant qu'il n'est pas calibré (la formule se réduit alors au terme NDVI).
"""

from app.utils.tree_co2_utils import calculate_biomass_and_co2

G_M2_TO_T_HA = 0.01

# ⚠️ Coefficient "x" de la formule cacao, à renseigner dès qu'il est connu.
COCOA_NDII_COEF = 0.0

# Chave et al. (2014) : AGB = 0.0673 × (ρ D² H)^0.976
COFFEE_CHAVE_A   = 0.0673
COFFEE_CHAVE_EXP = 0.976
COFFEE_DEFAULT_WOOD_DENSITY = 0.6  # g/cm³, valeur indicative Coffea spp. — surcharger si mesurée


def _maize(ix):
    return 45.2 + 310.5 * ix['ndvi']


def _rice(ix):
    return 120.3 + 250.7 * ix['evi']


def _wheat(ix):
    return -80 + 400 * ix['ndvi'] + 180 * ix['savi']


def _cocoa(ix):
    return 25 + 280 * ix['ndvi'] + COCOA_NDII_COEF * ix['ndmi']


# indices = clés des lignes Sentinel (_parse_response) ; 'ndmi' sert de NDII.
INDEX_MODELS = {
    'maize': {'indices': ('ndvi',),        'fn': _maize, 'formula': '45.2 + 310.5 × NDVI'},
    'rice':  {'indices': ('evi',),         'fn': _rice,  'formula': '120.3 + 250.7 × EVI'},
    'wheat': {'indices': ('ndvi', 'savi'), 'fn': _wheat, 'formula': '-80 + 400 × NDVI + 180 × SAVI'},
    'cocoa': {'indices': ('ndvi', 'ndmi'), 'fn': _cocoa,
              'formula': f'25 + 280 × NDVI + {COCOA_NDII_COEF} × NDII'},
}

SUPPORTED_CROPS = ('maize', 'rice', 'wheat', 'coffee', 'cocoa')

# Noms de Crop.name rencontrés (EN/FR, variétés) → clé de modèle
_CROP_ALIASES = {
    'maize': ('maize', 'corn', 'maïs', 'mais'),
    'rice':  ('rice', 'paddy', 'riz'),
    'wheat': ('wheat', 'blé', 'ble'),
    'coffee': ('coffee', 'café', 'cafe', 'arabica', 'robusta'),
    'cocoa': ('cocoa', 'cacao'),
}


def resolve_crop_key(crop_name):
    """'Coffee Arabica' → 'coffee', 'Maïs' → 'maize'. None si culture non supportée."""
    if not crop_name:
        return None
    name = str(crop_name).strip().lower()
    for key, aliases in _CROP_ALIASES.items():
        if any(a in name for a in aliases):
            return key
    return None


def _index_value(row, idx):
    """Accepte les lignes brutes (float) et le format guest {value, raw, oob, tier}."""
    v = row.get(idx)
    return v.get('value') if isinstance(v, dict) else v


def biomass_from_indices(crop_key, row):
    """
    Biomasse (g/m²) d'une ligne d'indices pour une culture "indice". Renvoie
    None si un indice requis manque (nuages) — jamais d'exception sur une ligne.
    """
    model = INDEX_MODELS[crop_key]
    ix = {}
    for idx in model['indices']:
        val = _index_value(row, idx)
        if val is None:
            return None
        ix[idx] = float(val)
    return max(0.0, model['fn'](ix))


def coffee_agb_per_tree_kg(dbh_cm, height_m, wood_density=COFFEE_DEFAULT_WOOD_DENSITY):
    """AGB d'un caféier (kg) — Chave et al. (2014)."""
    return COFFEE_CHAVE_A * (wood_density * dbh_cm ** 2 * height_m) ** COFFEE_CHAVE_EXP


def compute_crop_biomass(crop_name, history_rows, area_ha,
                         dbh_cm=None, height_m=None, wood_density=None, number_of_trees=None):
    """
    Point d'entrée : biomasse de la parcelle pour la culture donnée.

    history_rows : lignes Sentinel {date, ndvi, evi, savi, ndmi, ...} (brutes ou guest)
    area_ha      : surface de la parcelle (ha)
    Café         : dbh_cm, height_m (obligatoires), wood_density, number_of_trees

    Retourne (result_dict, error_message).
    """
    crop_key = resolve_crop_key(crop_name)
    if not crop_key:
        return None, (f"No biomass model for crop '{crop_name}'. "
                      f"Supported crops: {', '.join(SUPPORTED_CROPS)}.")
    if not area_ha or area_ha <= 0:
        return None, 'Could not compute parcel area'

    if crop_key == 'coffee':
        try:
            dbh_cm = float(dbh_cm) if dbh_cm not in (None, '') else None
            height_m = float(height_m) if height_m not in (None, '') else None
            wood_density = float(wood_density) if wood_density not in (None, '') else None
            number_of_trees = int(number_of_trees) if number_of_trees not in (None, '') else None
        except (TypeError, ValueError):
            return None, 'dbh_cm, height_m, wood_density and trees must be numbers.'
        if not dbh_cm or not height_m:
            return None, 'Coffee biomass requires dbh_cm (stem diameter, cm) and height_m (tree height, m).'
        if not number_of_trees:
            return None, 'Coffee biomass requires the number of trees (FarmData.number_of_tree or ?trees=).'
        rho = wood_density or COFFEE_DEFAULT_WOOD_DENSITY
        per_tree_kg = coffee_agb_per_tree_kg(dbh_cm, height_m, rho)
        agb_total_kg = per_tree_kg * number_of_trees
        result = calculate_biomass_and_co2(agb_total_kg)
        result.update({
            'crop':              crop_key,
            'crop_name':         crop_name,
            'method':            'allometric',
            'formula':           f'{COFFEE_CHAVE_A} × (ρ × DBH² × H)^{COFFEE_CHAVE_EXP}',
            'inputs':            {'wood_density': rho, 'dbh_cm': dbh_cm, 'height_m': height_m,
                                  'number_of_trees': number_of_trees},
            'agb_per_tree_kg':   round(per_tree_kg, 4),
            'area_ha':           round(area_ha, 4),
            'agb_t_per_ha':      round(agb_total_kg / 1000.0 / area_ha, 4),
        })
        return result, None

    model = INDEX_MODELS[crop_key]
    history = []
    for row in history_rows or []:
        g_m2 = biomass_from_indices(crop_key, row)
        if g_m2 is not None:
            history.append({
                'date':         row.get('date'),
                'biomass_g_m2': round(g_m2, 2),
                'agb_t_per_ha': round(g_m2 * G_M2_TO_T_HA, 4),
                **{idx: _index_value(row, idx) for idx in model['indices']},
            })
    if not history:
        needed = ' + '.join(i.upper() if i != 'ndmi' else 'NDII' for i in model['indices'])
        return None, f'No cloud-free {needed} reading available for this parcel'

    history.sort(key=lambda h: h['date'] or '')
    latest = history[-1]
    agb_total_kg = latest['agb_t_per_ha'] * area_ha * 1000.0
    result = calculate_biomass_and_co2(agb_total_kg)
    result.update({
        'crop':          crop_key,
        'crop_name':     crop_name,
        'method':        'satellite_index',
        'formula':       model['formula'],
        'indices_used':  {idx: latest[idx] for idx in model['indices']},
        'index_date':    latest['date'],
        'biomass_g_m2':  latest['biomass_g_m2'],
        'agb_t_per_ha':  latest['agb_t_per_ha'],
        'area_ha':       round(area_ha, 4),
        'history':       history,
    })
    if crop_key == 'cocoa' and COCOA_NDII_COEF == 0:
        result['warning'] = 'NDII coefficient (x) not calibrated yet: cocoa biomass uses the NDVI term only.'
    return result, None
