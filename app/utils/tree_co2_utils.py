"""
tree_co2_utils.py
──────────────────────────────────────────────────────────────────────────────
Calcul de la séquestration de CO2 par arbre, basé sur :
  1) Formule AGB (Above-Ground Biomass) à partir du diamètre et de la hauteur
     mesurés — donne la biomasse/CO2 "réelle" actuelle de l'arbre.
  2) Courbe sigmoid (logistique) par espèce — donne la trajectoire de
     croissance attendue et permet d'estimer le taux annuel de séquestration
     à un âge donné.

Hypothèses d'unités (à ajuster si besoin) :
  - Tree.diameter est en cm, Tree.height est en m (métrique).
  - La formule AGB source est en unités impériales (D en inch, H en ft),
    donc conversion cm→inch et m→ft est appliquée avant calcul.

Placer ce fichier dans app/utils/tree_co2_utils.py
"""

import math
from datetime import date

from app.models import Tree, SpeciesGrowthParams

# ── Constantes de conversion ────────────────────────────────────────────────
CM_TO_IN = 0.393701
M_TO_FT  = 3.28084

# ── Constantes biomasse → carbone (cf. article EcoMatcher) ─────────────────
BGB_RATIO        = 0.20   # BGB = 20% de l'AGB
DRY_MATTER_RATIO = 0.725  # 72.5% de matière sèche
CARBON_RATIO     = 0.5    # 50% du poids sec est du carbone
CO2_C_RATIO      = 3.67   # ratio masse molaire CO2/C (44/12)

# Paramètres sigmoid par défaut si l'espèce n'est pas dans SpeciesGrowthParams
DEFAULT_GROWTH_PARAMS = {'km': 0.25, 't_half': 10.0, 'mmax': 500.0}


# ══════════════════════════════════════════════════════════════════════════════
# 1) AGB / BIOMASSE / CO2 — à partir des mesures réelles (diamètre, hauteur)
# ══════════════════════════════════════════════════════════════════════════════

def calculate_agb(diameter_cm: float, height_m: float) -> float:
    """
    AGB (Above-Ground Biomass) en kg, à partir du diamètre (cm) et de la
    hauteur (m) mesurés sur l'arbre.

    Formule source (impériale) : AGB(lb) = 0.25 * D(in)^2 * H(ft)
    """
    d_in = diameter_cm * CM_TO_IN
    h_ft = height_m * M_TO_FT
    agb_lb = 0.25 * (d_in ** 2) * h_ft
    return agb_lb * 0.453592  # lb -> kg


def calculate_biomass_and_co2(agb_kg: float) -> dict:
    """
    À partir de l'AGB (kg), calcule BGB, biomasse totale, poids sec,
    carbone total et équivalent CO2 (tous en kg).
    """
    bgb_kg = BGB_RATIO * agb_kg
    total_biomass_kg = agb_kg + bgb_kg               # = 1.2 * AGB
    dry_weight_kg     = total_biomass_kg * DRY_MATTER_RATIO
    total_carbon_kg   = dry_weight_kg * CARBON_RATIO
    co2_kg            = total_carbon_kg * CO2_C_RATIO

    return {
        'agb_kg':            round(agb_kg, 4),
        'bgb_kg':             round(bgb_kg, 4),
        'total_biomass_kg':   round(total_biomass_kg, 4),
        'dry_weight_kg':      round(dry_weight_kg, 4),
        'total_carbon_kg':    round(total_carbon_kg, 4),
        'co2_sequestered_kg': round(co2_kg, 4),
    }


def calculate_tree_age_years(date_planted: date, reference_date: date = None) -> float:
    """Âge de l'arbre en années (décimal), depuis date_planted."""
    if not date_planted:
        return 0.0
    ref = reference_date or date.today()
    days = (ref - date_planted).days
    return max(days / 365.25, 0.0)


def calculate_tree_co2_measured(diameter_cm: float, height_m: float,
                                 date_planted: date, reference_date: date = None) -> dict:
    """
    Calcul complet "mesuré" pour un arbre : biomasse/CO2 totale sur la vie
    de l'arbre + taux annuel moyen (CO2 total / âge).
    """
    agb_kg = calculate_agb(diameter_cm, height_m)
    result = calculate_biomass_and_co2(agb_kg)

    age_years = calculate_tree_age_years(date_planted, reference_date)
    result['age_years'] = round(age_years, 2)
    result['co2_annual_avg_kg'] = (
        round(result['co2_sequestered_kg'] / age_years, 4) if age_years > 0 else 0.0
    )
    return result


# ══════════════════════════════════════════════════════════════════════════════
# 2) COURBE SIGMOID — trajectoire de croissance attendue par espèce
# ══════════════════════════════════════════════════════════════════════════════

def get_species_growth_params(species_name: str) -> dict:
    """
    Récupère (km, t_half, mmax) pour une espèce depuis SpeciesGrowthParams.
    Retombe sur des valeurs génériques par défaut si l'espèce n'existe pas.
    """
    if species_name:
        row = SpeciesGrowthParams.query.filter_by(species_name=species_name).first()
        if row:
            return {'km': row.km, 't_half': row.t_half, 'mmax': row.mmax}
    return dict(DEFAULT_GROWTH_PARAMS)


def sigmoid_biomass(t: float, km: float, t_half: float, mmax: float) -> float:
    """
    Biomasse totale attendue (kg) à l'âge t (années), selon le modèle
    logistique :  M(t) = Mmax / (1 + exp(-Km * (t - t_half)))
    """
    if t <= 0:
        return 0.0
    exponent = -km * (t - t_half)
    # Protection contre l'overflow pour de grandes valeurs
    exponent = max(min(exponent, 700), -700)
    return mmax / (1 + math.exp(exponent))


def sigmoid_annual_co2_rate(age_years: float, species_params: dict) -> dict:
    """
    Taux de séquestration CO2 annuel (kg/an) prédit par la courbe sigmoid,
    à l'âge donné : différence de biomasse prédite entre t-1 et t,
    convertie en CO2 via la même chaîne AGB->BGB->TDW->TC->CO2.
    """
    km, t_half, mmax = species_params['km'], species_params['t_half'], species_params['mmax']

    m_t      = sigmoid_biomass(age_years, km, t_half, mmax)
    m_t_prev = sigmoid_biomass(max(age_years - 1, 0), km, t_half, mmax)
    delta_biomass_kg = max(m_t - m_t_prev, 0.0)

    # delta_biomass_kg représente déjà la biomasse totale (AGB+BGB) incrémentale
    dry_weight_kg   = delta_biomass_kg * DRY_MATTER_RATIO
    total_carbon_kg = dry_weight_kg * CARBON_RATIO
    co2_kg          = total_carbon_kg * CO2_C_RATIO

    return {
        'predicted_total_biomass_kg': round(m_t, 4),
        'delta_biomass_kg':           round(delta_biomass_kg, 4),
        'co2_annual_rate_sigmoid_kg': round(co2_kg, 4),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 3) API haut niveau — par arbre / par forêt
# ══════════════════════════════════════════════════════════════════════════════

def compute_tree_co2_full(tree: Tree, reference_date: date = None) -> dict:
    """
    Combine le calcul mesuré (AGB via diamètre/hauteur) et la prédiction
    sigmoid (courbe de croissance de l'espèce) pour un arbre donné.
    """
    measured = calculate_tree_co2_measured(
        diameter_cm=tree.diameter,
        height_m=tree.height,
        date_planted=tree.date_planted,
        reference_date=reference_date,
    )

    species_params = get_species_growth_params(tree.type)
    sigmoid_result = sigmoid_annual_co2_rate(measured['age_years'], species_params)

    return {
        'tree_id':      tree.id,
        'name':         tree.name,
        'species':      tree.type,
        'diameter_cm':  tree.diameter,
        'height_m':     tree.height,
        'date_planted': tree.date_planted.isoformat() if tree.date_planted else None,
        **measured,
        'growth_params': species_params,
        **sigmoid_result,
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4) AGB/BGB FORÊT ENTIÈRE — à partir d'un indice satellite (NDVI), quand on
#    n'a PAS de mesures diamètre/hauteur arbre-par-arbre (cas typique : forêt
#    non inventoriée, estimation par imagerie Sentinel-2 seule).
# ══════════════════════════════════════════════════════════════════════════════

# Modèle exponentiel générique AGB(Mg/ha) = NDVI_AGB_A * exp(NDVI_AGB_B * NDVI).
# ⚠️ Calibration ILLUSTRATIVE (pas issue d'une étude de terrain locale) : ancrée
# sur NDVI≈0.2 (végétation clairsemée) → ~5 Mg/ha et NDVI≈0.9 (forêt tropicale
# dense) → ~400 Mg/ha, une plage haute usuelle en littérature pour l'AGB de
# forêt tropicale dense. À recalibrer avec des parcelles d'inventaire locales
# (mesures diamètre/hauteur réelles, cf. calculate_agb ci-dessus) avant tout
# usage réglementaire — ce modèle est une estimation de dégrossissage, pas un
# remplacement des données GFW/inventaire terrain.
NDVI_AGB_A = 1.43
NDVI_AGB_B = 6.26


def calculate_agb_per_ha_from_ndvi(ndvi: float) -> float:
    """AGB (Mg/ha) estimé à partir du NDVI moyen d'une parcelle/forêt."""
    ndvi = max(0.0, min(1.0, ndvi or 0.0))
    return NDVI_AGB_A * math.exp(NDVI_AGB_B * ndvi)


def compute_forest_biomass_from_index(ndvi: float, area_ha: float, index_date: str = None) -> dict:
    """
    Biomasse forêt entière (AGB/BGB/CO2) estimée depuis le NDVI moyen (Sentinel-2)
    et la surface (ha) du polygone — même chaîne de conversion biomasse→CO2 que
    calculate_biomass_and_co2() (mesure arbre par arbre), pour rester cohérent
    dans toute l'app, seule la source de l'AGB change (indice satellite au lieu
    de diamètre/hauteur mesurés).
    """
    agb_per_ha_mg = calculate_agb_per_ha_from_ndvi(ndvi)
    agb_total_kg  = agb_per_ha_mg * area_ha * 1000.0  # Mg/ha -> kg total
    result = calculate_biomass_and_co2(agb_total_kg)
    result.update({
        'ndvi_used':     round(ndvi, 4) if ndvi is not None else None,
        'ndvi_date':     index_date,
        'area_ha':       round(area_ha, 4),
        'agb_per_ha_mg': round(agb_per_ha_mg, 2),
        'model':         f'AGB(Mg/ha) = {NDVI_AGB_A} * exp({NDVI_AGB_B} * NDVI) — generic estimate, requires local calibration',
    })
    return result


def compute_forest_co2_summary(forest_id: int, reference_date: date = None) -> dict:
    """
    Agrège le calcul CO2 (mesuré + sigmoid) sur tous les arbres vivants
    (date_cut is None) d'une forêt.
    """
    trees = Tree.query.filter_by(forest_id=forest_id, date_cut=None).all()

    trees_data = [compute_tree_co2_full(t, reference_date) for t in trees]

    totals = {
        'tree_count':               len(trees_data),
        'total_co2_sequestered_kg': round(sum(t['co2_sequestered_kg'] for t in trees_data), 4),
        'total_co2_annual_avg_kg':  round(sum(t['co2_annual_avg_kg'] for t in trees_data), 4),
        'total_co2_annual_sigmoid_kg': round(sum(t['co2_annual_rate_sigmoid_kg'] for t in trees_data), 4),
    }

    return {'trees': trees_data, 'totals': totals}