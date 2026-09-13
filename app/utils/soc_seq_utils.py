"""
soc_seq_utils.py
──────────────────────────────────────────────────────────────────────────────
FAO GSOCseq (Global Soil Organic Carbon Sequestration Potential Map, v1.1) —
scénario SSM3 (Sustainable Soil Management), profondeur 0-30cm.

Contrairement au SOC ISRIC SoilGrids actuel (_fetch_soc_soilgrids), qui ne
requête qu'un point (le centroïde de la ferme), ce module fait une vraie
statistique zonale (moyenne) sur l'intégralité du polygone de la ferme, à
partir des deux GeoTIFF globaux SSM3 téléchargés une fois pour toutes depuis :
  http://54.229.242.119/GSOCseqv1.1/GSOCseq_finalSOC_SSM3_Map030.tif
  http://54.229.242.119/GSOCseqv1.1/GSOCseq_RSR_SSM3_Map030.tif
(placés dans app/data/gsocseq/, non versionnés — voir .gitignore).

Aucun appel réseau à l'exécution : les rasters sont locaux, la stat zonale
est rapide même répétée pour de nombreuses fermes.
"""
import os
from rasterstats import zonal_stats

DATA_DIR       = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'gsocseq')
FINAL_SOC_TIF  = os.path.join(DATA_DIR, 'GSOCseq_finalSOC_SSM3_Map030.tif')
RSR_TIF        = os.path.join(DATA_DIR, 'GSOCseq_RSR_SSM3_Map030.tif')

SOURCE_LABEL = 'FAO GSOCseq v1.1 — Scenario SSM3 (Sustainable Soil Management), 0-30cm'


def _zonal_mean(tif_path: str, geometry: dict) -> float | None:
    """Moyenne de la bande raster sur la géométrie donnée, ou None si indisponible."""
    if not os.path.exists(tif_path):
        return None
    try:
        stats = zonal_stats(geometry, tif_path, stats=['mean'], all_touched=True)
        if not stats or stats[0].get('mean') is None:
            return None
        return round(float(stats[0]['mean']), 3)
    except Exception as e:
        print(f"[soc_seq_utils] zonal_stats échec sur {os.path.basename(tif_path)} : {e}")
        return None


def is_available() -> bool:
    """True si les deux GeoTIFF ont bien été téléchargés sur le serveur."""
    return os.path.exists(FINAL_SOC_TIF) and os.path.exists(RSR_TIF)


def get_gsocseq_ssm3(geometry: dict) -> dict:
    """
    geometry : dict GeoJSON Polygon (ex: sortie de sentinel_utils._build_geometry).
    Retourne le stock final de carbone organique du sol (t/ha) et le taux de
    séquestration relatif (%) attendus sous scénario SSM3, moyennés sur le
    polygone fourni.
    """
    if not geometry or geometry.get('type') != 'Polygon':
        return {
            'final_soc_stock_t_ha': None,
            'relative_sequestration_rate_pct': None,
            'available': False,
            'source': SOURCE_LABEL,
        }

    return {
        'final_soc_stock_t_ha':             _zonal_mean(FINAL_SOC_TIF, geometry),
        'relative_sequestration_rate_pct':  _zonal_mean(RSR_TIF, geometry),
        'available': is_available(),
        'source': SOURCE_LABEL,
    }
