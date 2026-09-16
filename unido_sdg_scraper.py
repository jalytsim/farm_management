#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unido_sdg_scraper.py
=====================

Recupere automatiquement, pour une liste de pays, les 11 indicateurs retenus
pour Madagascar (fichier 11_indicateurs_retenus_Madagascar.xlsx) a partir de
DEUX sources publiques (aucune cle API requise) :

    1) UNIDO Statistics Data Portal (stat.unido.org) :
       - dataset "CIP"  (Competitive Industrial Performance index)
       - dataset "SDG"  (indicateurs officiels SDG 9)
    2) World Bank Open Data (api.worldbank.org) :
       - pour le PIB et la VAM en NIVEAU (dollars constants), qui n'existent
         pas en tant que tels dans les bases ONUDI ci-dessus.

Et produit un classeur Excel :
    - une feuille par pays (11 indicateurs en lignes, annees en colonnes),
    - une feuille "Comparaison" en tete de classeur qui rassemble tous les
      pays sous chaque indicateur (facile a filtrer / comparer).

Ce mapping (quel indicateur vient de quelle source/quel code) a ete VERIFIE
en interrogeant directement les deux API ONUDI :

    CIP score                                              -> CIP / cip
    CIP rank                                                -> CIP / cipRank
    Medium- and high-tech MVA share in total MVA            -> CIP / MHVAsh
    Medium- and high-tech manuf. exports share in total...  -> CIP / MHXsh
    Manufacturing value added per capita                    -> CIP / MVApc
    Manufacturing value added share in total GDP            -> CIP / MVAsh
    GDP (Gross Domestic Product), constant USD               -> World Bank / NY.GDP.MKTP.KD
    MVA (Manufacturing Value Added), constant USD             -> World Bank / NV.IND.MANF.KD
    Manufacturing employment as a proportion of total emp.   -> SDG / "9.2.2 ... employment ..."
    CO2 emissions per unit of manufacturing value added      -> SDG / "9.4.1 ... per unit ..."

IMPORTANT
---------
Ce script doit etre execute depuis une machine ayant acces a Internet vers
stat.unido.org ET api.worldbank.org (aucune cle API necessaire pour les deux).

Installation
------------
    pip install requests openpyxl

Utilisation
-----------
    python unido_sdg_scraper.py                    # genere le fichier Excel
    python unido_sdg_scraper.py --discover-cip      # liste les variables CIP
    python unido_sdg_scraper.py --discover-sdg      # liste les variables SDG9
    python unido_sdg_scraper.py --discover-countries
    python unido_sdg_scraper.py --debug             # sauvegarde les reponses
                                                      # brutes dans ./debug/

Personnalisation
----------------
Modifiez simplement COUNTRIES et YEARS ci-dessous.
"""

import argparse
import json
import time
from pathlib import Path

import requests
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# --------------------------------------------------------------------------- #
# CONFIGURATION - a adapter selon vos besoins
# --------------------------------------------------------------------------- #

# Noms des pays TELS QU'ILS APPARAISSENT dans la base ONUDI (nom anglais
# officiel). Utilisez --discover-countries pour la liste complete.
COUNTRIES = [
    "Madagascar",
    "Brazil",
    "Viet Nam",
    "Senegal",
    "Ethiopia",
]

# Plage d'annees a recuperer (comme dans le fichier Madagascar : 1990-2025)
YEARS = [str(y) for y in range(1990, 2026)]

UNIDO_BASE = "https://stat.unido.org/portal"
WB_BASE = "https://api.worldbank.org/v2"
OUTPUT_FILE = "indicateurs_SDG9_comparaison.xlsx"
DEBUG_DIR = Path("debug")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# --------------------------------------------------------------------------- #
# Table de correspondance indicateur -> source (VERIFIEE, voir en-tete)
# --------------------------------------------------------------------------- #
# type "CIP"  : code exact dans le dataset CIP de l'ONUDI
# type "SDG"  : sous-chaine(s) distinctive(s) a chercher dans les libelles
#               officiels du dataset SDG9 de l'ONUDI (insensible a la casse)
# type "WB"   : indicateur de l'API World Bank Open Data

INDICATORS = [
    {"label": "CIP score", "type": "CIP", "code": "cip"},
    {"label": "CIP rank", "type": "CIP", "code": "cipRank"},
    {"label": "Medium- and high-tech MVA share in total MVA", "type": "CIP", "code": "MHVAsh"},
    {"label": "Medium- and high-tech manufactured exports share in total manufactured exports",
     "type": "CIP", "code": "MHXsh"},
    {"label": "Manufacturing value added per capita", "type": "CIP", "code": "MVApc"},
    {"label": "Manufacturing value added share in total GDP", "type": "CIP", "code": "MVAsh"},
    {"label": "GDP (Gross Domestic Product), constant USD", "type": "WB", "code": "NY.GDP.MKTP.KD"},
    {"label": "MVA (Manufacturing Value Added), constant USD", "type": "WB", "code": "NV.IND.MANF.KD"},
    # Codes SDG9 verifies directement sur un export brut de l'API (fichier
    # unido_sdg_meta_brut.json fourni par l'utilisateur) : plus de recherche
    # par sous-chaine, plus d'ambiguite possible.
    {"label": "Manufacturing employment as a proportion of total employment (%)",
     "type": "SDG", "code": "SL_TLF_MANF"},
    {"label": "Carbon dioxide emissions per unit of manufacturing value added "
              "(kilogrammes of CO2 per constant 2020 United States dollars)",
     "type": "SDG", "code": "EN_ATM_CO2MVA"},
]


# --------------------------------------------------------------------------- #
# 1. ONUDI : metadonnees (pays + variables) et donnees
# --------------------------------------------------------------------------- #

def get_unido_dataset(dataset_name: str) -> dict:
    """GET /dataset/getDataset/{name} -> id, pays, variables du jeu de donnees."""
    url = f"{UNIDO_BASE}/dataset/getDataset/{dataset_name}"
    resp = SESSION.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_country_index(meta: dict) -> dict:
    """{'madagascar': {'c': '450', 'iso3': 'MDG'}, ...}"""
    out = {}
    for c in meta.get("countries", []):
        name = c.get("lang", {}).get("en", "").strip()
        if name and c.get("c"):
            out[name.lower()] = {"c": c["c"], "iso3": c.get("iso3", "").strip()}
    return out


def variable_code(v: dict) -> str:
    # La cle utilisee par l'API ONUDI pour le code de variable est "c"
    # (confirme empiriquement sur le dataset CIP).
    for k in ("c", "code", "variableCode", "var", "id"):
        if k in v and isinstance(v[k], str):
            return v[k]
    return ""


def variable_label(v: dict) -> str:
    if isinstance(v.get("lang"), dict):
        lbl = v["lang"].get("en", "")
        if lbl:
            return lbl
    for k in ("name", "label", "description"):
        val = v.get(k)
        if isinstance(val, str) and val:
            return val
    return ""


def fetch_unido_country_data(dataset_id, country_code, variable_codes, periods,
                              debug=False, tag=""):
    """POST /dataset/getDataWithoutActivities pour UN pays et une liste de
    codes de variables d'un meme dataset (contrainte de l'API : un appel par
    pays)."""
    if not variable_codes:
        return {}
    url = f"{UNIDO_BASE}/dataset/getDataWithoutActivities"
    payload = {
        "datasetId": dataset_id,
        "countryCode": country_code,
        "fullPrecision": True,
        "variableCodes": variable_codes,
        "periods": periods,
    }
    resp = SESSION.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if debug:
        DEBUG_DIR.mkdir(exist_ok=True)
        (DEBUG_DIR / f"raw_unido_{tag}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    return data


def extract_unido_series(raw, variable_codes, periods) -> dict:
    """Parcours generique et tolerant de la reponse getDataWithoutActivities :
    on rassemble tout triplet (code_variable, annee, valeur) reconnaissable,
    quelle que soit la forme exacte (non documentee en detail) du JSON.
    Si le resultat est vide, relancez avec --debug et inspectez
    debug/raw_unido_*.json pour adapter cette fonction si necessaire."""
    var_set = set(variable_codes)
    year_set = set(periods)
    out = {v: {} for v in variable_codes}

    def maybe_record(d: dict):
        code = None
        for k in ("c", "variableCode", "code", "var", "variable"):
            if k in d and d[k] in var_set:
                code = d[k]
                break
        if code is None:
            return
        period = None
        for k in ("period", "year", "p", "y", "periodCode", "time"):
            if k in d:
                p = str(d[k])
                if p in year_set:
                    period = p
                    break
        if period is None:
            return
        value = None
        for k in ("value", "val", "v", "obsValue", "data"):
            if k in d and isinstance(d[k], (int, float)):
                value = d[k]
                break
        if value is not None:
            out[code][period] = value

    def walk(node):
        if isinstance(node, dict):
            maybe_record(node)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(raw)
    return out


# --------------------------------------------------------------------------- #
# 2. World Bank Open Data (API REST publique, sans cle)
# --------------------------------------------------------------------------- #

def fetch_worldbank_series(iso3: str, indicator: str, years: list,
                            debug=False, tag="") -> dict:
    """GET /country/{iso3}/indicator/{indicator}?date=YYYY:YYYY&format=json
    Retourne {annee: valeur}."""
    if not iso3:
        return {}
    date_range = f"{years[0]}:{years[-1]}"
    url = f"{WB_BASE}/country/{iso3}/indicator/{indicator}"
    params = {"date": date_range, "format": "json", "per_page": "20000"}
    resp = SESSION.get(url, params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()

    if debug:
        DEBUG_DIR.mkdir(exist_ok=True)
        (DEBUG_DIR / f"raw_wb_{tag}_{indicator}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    out = {}
    if isinstance(payload, list) and len(payload) > 1 and payload[1]:
        for row in payload[1]:
            year = str(row.get("date"))
            val = row.get("value")
            if year in years and val is not None:
                out[year] = val
    return out


# --------------------------------------------------------------------------- #
# 3. Construction du classeur Excel
# --------------------------------------------------------------------------- #

HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", name="Arial", size=10)
LABEL_FONT = Font(bold=True, name="Arial", size=10)
CELL_FONT = Font(name="Arial", size=10)
COUNTRY_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")


def write_country_sheet(wb, country_name, indicator_labels, years, series_by_indicator):
    ws = wb.create_sheet(title=country_name[:31])  # 31 = limite Excel
    ws.cell(row=1, column=1,
            value=f"{country_name} — indicateurs industriels (ONUDI CIP/SDG9 + Banque Mondiale)").font = Font(
        bold=True, size=12, name="Arial"
    )
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(years) + 1)

    header_row = 2
    ws.cell(row=header_row, column=1, value="Indicateur").font = HEADER_FONT
    ws.cell(row=header_row, column=1).fill = HEADER_FILL
    for j, year in enumerate(years, start=2):
        c = ws.cell(row=header_row, column=j, value=int(year))
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center")

    for i, label in enumerate(indicator_labels, start=header_row + 1):
        c = ws.cell(row=i, column=1, value=label)
        c.font = LABEL_FONT
        c.alignment = Alignment(wrap_text=True, vertical="center")
        values = series_by_indicator.get(label, {})
        for j, year in enumerate(years, start=2):
            v = values.get(year)
            cell = ws.cell(row=i, column=j, value=v)
            cell.font = CELL_FONT
            cell.number_format = "0.######"

    ws.freeze_panes = ws.cell(row=header_row + 1, column=2).coordinate
    ws.column_dimensions["A"].width = 48
    for j in range(2, len(years) + 2):
        ws.column_dimensions[get_column_letter(j)].width = 10

    return ws


def write_comparison_sheet(wb, countries, indicator_labels, years, all_series):
    ws = wb.create_sheet(title="Comparaison", index=0)
    ws.cell(row=1, column=1,
            value="Comparaison entre pays — indicateurs industriels (ONUDI + Banque Mondiale)").font = Font(
        bold=True, size=12, name="Arial"
    )
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(years) + 2)

    header_row = 2
    headers = ["Indicateur", "Pays"] + [int(y) for y in years]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=header_row, column=j, value=h)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center", wrap_text=True)

    row = header_row + 1
    for label in indicator_labels:
        for country in countries:
            ws.cell(row=row, column=1, value=label).font = CELL_FONT
            country_cell = ws.cell(row=row, column=2, value=country)
            country_cell.font = LABEL_FONT
            country_cell.fill = COUNTRY_FILL
            values = all_series.get(country, {}).get(label, {})
            for j, year in enumerate(years, start=3):
                v = values.get(year)
                cell = ws.cell(row=row, column=j, value=v)
                cell.font = CELL_FONT
                cell.number_format = "0.######"
            row += 1

    ws.freeze_panes = ws.cell(row=header_row + 1, column=3).coordinate
    ws.column_dimensions["A"].width = 48
    ws.column_dimensions["B"].width = 22
    for j in range(3, len(years) + 3):
        ws.column_dimensions[get_column_letter(j)].width = 10

    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(years) + 2)}{row - 1}"
    return ws


# --------------------------------------------------------------------------- #
# 4. Orchestration
# --------------------------------------------------------------------------- #

SCRIPT_VERSION = "v3 (codes CIP/SDG9 verifies et code en dur, plus de matching flou)"


def run(discover_cip=False, discover_sdg=False, discover_countries=False,
        debug=False, output=OUTPUT_FILE):
    print(f"=== unido_sdg_scraper.py — {SCRIPT_VERSION} ===")
    print("Connexion aux portails ONUDI (CIP + SDG9)…")
    cip_meta = get_unido_dataset("CIP")
    sdg_meta = get_unido_dataset("SDG")
    cip_id, sdg_id = cip_meta["id"], sdg_meta["id"]
    cip_vars = cip_meta.get("variables", [])
    sdg_vars = sdg_meta.get("variables", [])
    print(f"  -> dataset CIP id={cip_id} ({len(cip_vars)} variables)")
    print(f"  -> dataset SDG id={sdg_id} ({len(sdg_vars)} variables)")

    if discover_cip:
        print("\nVariables CIP disponibles (code : libelle) :")
        for v in cip_vars:
            print(f"  - {variable_code(v):<15} : {variable_label(v)}")
        return
    if discover_sdg:
        print("\nVariables SDG9 disponibles (code : libelle) :")
        for v in sdg_vars:
            print(f"  - {variable_code(v):<15} : {variable_label(v)}")
        return

    # les deux datasets partagent la meme liste de pays UNIDO -> on prend CIP
    country_index = build_country_index(cip_meta)
    # au cas ou un pays serait present uniquement cote SDG :
    for k, v in build_country_index(sdg_meta).items():
        country_index.setdefault(k, v)

    if discover_countries:
        print("\nPays disponibles dans la base ONUDI :")
        for name in sorted(country_index):
            print(" -", name.title())
        return

    # verification que les codes codes en dur existent bien dans le dataset
    # recupere (alerte si l'ONUDI a change un code depuis la redaction du
    # script, plutot que d'echouer silencieusement)
    known_cip_codes = {variable_code(v) for v in cip_vars}
    known_sdg_codes = {variable_code(v) for v in sdg_vars}
    for ind in INDICATORS:
        if ind["type"] == "CIP" and ind["code"] not in known_cip_codes:
            print(f"[ATTENTION] Code CIP '{ind['code']}' introuvable dans le dataset actuel !")
        if ind["type"] == "SDG" and ind["code"] not in known_sdg_codes:
            print(f"[ATTENTION] Code SDG '{ind['code']}' introuvable dans le dataset actuel !")

    print("\nCorrespondance indicateur -> source :")
    for ind in INDICATORS:
        status = ind.get("code") or "NON TROUVE"
        print(f"  - [{ind['type']:>3}] {ind['label'][:65]:<65} -> {status}")
    if any(not ind.get("code") for ind in INDICATORS):
        print(
            "\n[ATTENTION] Un ou plusieurs indicateurs SDG n'ont pas ete retrouves.\n"
            "Lancez 'python unido_sdg_scraper.py --discover-sdg' pour voir tous les\n"
            "libelles disponibles et ajustez la liste 'match' dans INDICATORS."
        )

    cip_codes = [i["code"] for i in INDICATORS if i["type"] == "CIP" and i.get("code")]
    sdg_codes = [i["code"] for i in INDICATORS if i["type"] == "SDG" and i.get("code")]

    wb = Workbook()
    wb.remove(wb.active)

    all_series = {}
    valid_countries = []

    for country in COUNTRIES:
        key = country.lower()
        if key not in country_index:
            print(f"[ATTENTION] Pays introuvable dans la base ONUDI : {country} (ignore)")
            continue
        info = country_index[key]
        country_code, iso3 = info["c"], info["iso3"]
        tag = country.replace(" ", "_")
        print(f"Telechargement des donnees pour {country} (ONUDI={country_code}, ISO3={iso3})…")

        cip_raw = fetch_unido_country_data(cip_id, country_code, cip_codes, YEARS,
                                            debug=debug, tag=f"CIP_{tag}")
        cip_series = extract_unido_series(cip_raw, cip_codes, YEARS)
        time.sleep(0.3)

        sdg_raw = fetch_unido_country_data(sdg_id, country_code, sdg_codes, YEARS,
                                            debug=debug, tag=f"SDG_{tag}")
        sdg_series = extract_unido_series(sdg_raw, sdg_codes, YEARS)
        time.sleep(0.3)

        by_label = {}
        for ind in INDICATORS:
            label = ind["label"]
            if ind["type"] == "CIP":
                by_label[label] = cip_series.get(ind.get("code"), {})
            elif ind["type"] == "SDG":
                by_label[label] = sdg_series.get(ind.get("code"), {})
            elif ind["type"] == "WB":
                by_label[label] = fetch_worldbank_series(
                    iso3, ind["code"], YEARS, debug=debug, tag=tag
                )
                time.sleep(0.2)

        all_series[country] = by_label
        valid_countries.append(country)
        write_country_sheet(wb, country, [i["label"] for i in INDICATORS], YEARS, by_label)

    write_comparison_sheet(wb, valid_countries, [i["label"] for i in INDICATORS], YEARS, all_series)

    wb.save(output)
    print(f"\nTerminee ! Classeur enregistre : {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discover-cip", action="store_true",
                         help="Liste les variables du dataset CIP de l'ONUDI et quitte")
    parser.add_argument("--discover-sdg", action="store_true",
                         help="Liste les variables du dataset SDG9 de l'ONUDI et quitte")
    parser.add_argument("--discover-countries", action="store_true",
                         help="Liste les pays disponibles dans la base ONUDI et quitte")
    parser.add_argument("--debug", action="store_true",
                         help="Sauvegarde les reponses JSON brutes dans ./debug/ pour inspection")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Nom du fichier Excel de sortie")
    args = parser.parse_args()
    run(discover_cip=args.discover_cip, discover_sdg=args.discover_sdg,
        discover_countries=args.discover_countries, debug=args.debug, output=args.output)


if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------- #
# Si vous obtenez une erreur 403 (Cloudflare) sur stat.unido.org
# --------------------------------------------------------------------------- #
#
# La documentation officielle de l'API ONUDI (https://stat.unido.org/unido-
# statistics-portal-api) indique que Cloudflare peut, dans de rares cas,
# bloquer les clients HTTP simples. Si cela arrive :
#
#   pip install undetected-chromedriver selenium
#
# et pilotez un navigateur reel pour les requetes (voir l'exemple sur la
# page ci-dessus), ou executez le script depuis un autre reseau/poste.
# L'API World Bank (api.worldbank.org) n'a pas cette protection.
