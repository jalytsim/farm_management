#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unido_sdg_scraper.py
=====================

Recupere automatiquement, depuis le portail officiel de statistiques de l'ONUDI
(UNIDO Statistics Portal - https://stat.unido.org/data/download?dataset=sdg),
les 11 indicateurs "SDG9 / CIP" retenus pour Madagascar (fichier
11_indicateurs_retenus_Madagascar.xlsx) pour une liste de pays a comparer,
et produit un classeur Excel :

    - une feuille par pays (memes 11 indicateurs, annees en colonnes),
    - une feuille "Comparaison" qui rassemble tous les pays et tous les
      indicateurs dans un seul tableau facile a trier / filtrer.

IMPORTANT
---------
Ce script doit etre execute sur VOTRE machine (ou un serveur) qui a acces a
Internet vers stat.unido.org. Le portail utilise Cloudflare ; dans de rares
cas l'appel direct via `requests` peut etre bloque (erreur 403). Si cela
arrive, voir la section "Si vous obtenez une erreur 403" tout en bas de ce
fichier.

Installation
------------
    pip install requests openpyxl

Utilisation
-----------
    python unido_sdg_scraper.py                  # genere le fichier Excel
    python unido_sdg_scraper.py --discover        # liste les indicateurs
                                                    # disponibles dans la
                                                    # base SDG de l'ONUDI
    python unido_sdg_scraper.py --debug           # sauvegarde les reponses
                                                    # brutes de l'API dans
                                                    # ./debug/ pour inspection

Personnalisation
----------------
Modifiez simplement les constantes COUNTRIES et YEARS ci-dessous.
"""

import argparse
import difflib
import json
import re
import sys
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
# officiel). Utilisez --discover-countries pour voir la liste complete si un
# nom ne correspond pas.
COUNTRIES = [
    "Madagascar",
    "Brazil",
    "Viet Nam",
    "Senegal",
    "Ethiopia",
]

# Plage d'annees a recuperer (comme dans le fichier Madagascar : 1990-2025)
YEARS = [str(y) for y in range(1990, 2026)]

# Les 11 indicateurs retenus (libelles utilises dans le fichier Madagascar).
# Le script les met en correspondance automatiquement avec les codes de
# variables de la base SDG de l'ONUDI par similarite de texte.
INDICATOR_LABELS = [
    "CIP score",
    "CIP rank",
    "Medium- and high-tech MVA share in total MVA",
    "Medium- and high-tech manufactured exports share in total manufactured exports",
    "Manufacturing value added per capita",
    "Manufacturing value added share in total GDP",
    "GDP (Gross Domestic Product), constant 2020 USD",
    "MVA (Manufacturing Value Added), constant 2020 USD",
    "Manufacturing employment as a proportion of total employment (%)",
    "Carbon dioxide emissions per unit of manufacturing value added "
    "(kilogrammes of CO2 per constant 2020 United States dollars)",
]

DATASET_NAME = "SDG"  # nom du jeu de donnees sur le portail ONUDI
BASE_URL = "https://stat.unido.org/portal"
OUTPUT_FILE = "indicateurs_SDG9_comparaison.xlsx"
DEBUG_DIR = Path("debug")

HEADERS = {
    # Un user-agent "navigateur" reduit le risque de blocage par Cloudflare.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# --------------------------------------------------------------------------- #
# 1. Decouverte du jeu de donnees (pays + variables disponibles)
# --------------------------------------------------------------------------- #

def get_dataset_metadata(dataset_name: str = DATASET_NAME) -> dict:
    """GET /dataset/getDataset/{name} -> id, liste des pays, liste des
    variables disponibles. C'est cette reponse qui pilote tout le reste :
    on ne code jamais les identifiants en dur, on les redemande a chaque
    execution (l'ONUDI les fait evoluer)."""
    url = f"{BASE_URL}/dataset/getDataset/{dataset_name}"
    resp = SESSION.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_country_map(meta: dict) -> dict:
    """{'madagascar': '450', 'kenya': '404', ...} (cle normalisee -> code pays)"""
    out = {}
    for c in meta.get("countries", []):
        name = c.get("lang", {}).get("en", "").strip()
        code = c.get("c")
        if name and code:
            out[name.lower()] = code
    return out


def find_variable_list(meta: dict):
    """La documentation de l'API indique que la reponse contient une 'liste
    des variables avec leurs codes', mais le nom exact de la cle JSON peut
    varier. On cherche d'abord les cles evidentes, puis on scanne le reste
    de la structure pour tout objet qui ressemble a une variable
    (un code + un libelle)."""
    candidate_keys = [
        "variables", "variableList", "vars", "indicators", "indicatorList",
    ]
    for key in candidate_keys:
        if key in meta and isinstance(meta[key], list) and meta[key]:
            return meta[key]

    # Repli : parcours generique de tout le JSON a la recherche de listes
    # d'objets {code/name...} qui ne sont ni les pays ni les groupes.
    skip_keys = {"countries", "groups"}
    found = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in skip_keys:
                    continue
                walk(v)
        elif isinstance(node, list):
            if node and all(isinstance(i, dict) for i in node):
                sample = node[0]
                has_code = any(k in sample for k in ("code", "variableCode", "var"))
                has_name = any(k in sample for k in ("lang", "name", "label"))
                if has_code and has_name:
                    found.append(node)
            for i in node:
                walk(i)

    walk(meta)
    return found[0] if found else []


def variable_label(v: dict) -> str:
    if isinstance(v.get("lang"), dict):
        lbl = v["lang"].get("en", "")
        if lbl:
            return lbl
    for k in ("name", "label", "description", "text", "longName",
              "shortName", "title", "en"):
        val = v.get(k)
        if isinstance(val, str) and val:
            return val
    # dernier recours : le code lui-meme (mieux que rien pour le matching)
    return variable_code(v)


def variable_code(v: dict) -> str:
    for k in ("code", "variableCode", "var", "id", "key", "variable"):
        if k in v and isinstance(v[k], str):
            return v[k]
    return ""


# Mots-cles de repli bases sur les conventions de codes habituelles de
# l'ONUDI (utiles quand les libellés textuels de la variable sont absents
# ou tres differents de ceux du fichier Madagascar). Verifies/affines a la
# main si besoin apres avoir consulte --discover.
ALIAS_KEYWORDS = {
    "CIP score": ["cip"],
    "CIP rank": ["ciprank", "cip_rank", "rank"],
    "Medium- and high-tech MVA share in total MVA": ["mhvash"],
    "Medium- and high-tech manufactured exports share in total manufactured exports": ["mhxsh"],
    "Manufacturing value added per capita": ["mvapc"],
    "Manufacturing value added share in total GDP": ["mvash"],
    "GDP (Gross Domestic Product), constant 2020 USD": ["gdp"],
    "MVA (Manufacturing Value Added), constant 2020 USD": ["mva"],
    "Manufacturing employment as a proportion of total employment (%)": [
        "emp", "employment",
    ],
    "Carbon dioxide emissions per unit of manufacturing value added "
    "(kilogrammes of CO2 per constant 2020 United States dollars)": [
        "co2",
    ],
}


def match_indicators(variables: list, labels: list) -> dict:
    """Associe chaque libelle souhaite (fichier Madagascar) au code de
    variable de l'ONUDI. Deux passes :
      1) correspondance par mot-cle sur le CODE (ALIAS_KEYWORDS), la plus
         fiable puisque les codes de l'ONUDI sont stables ;
      2) a defaut, similarite textuelle sur le libelle (difflib).
    Retourne {libelle: code_variable_ou_None}.
    """
    by_code = {variable_code(v): v for v in variables if variable_code(v)}
    label_choices = {variable_label(v): variable_code(v) for v in variables if variable_label(v)}

    result = {}
    used_codes = set()

    for label in labels:
        code_found = None

        # Passe 1 : mots-cles sur le code
        for kw in ALIAS_KEYWORDS.get(label, []):
            for code in by_code:
                if code in used_codes:
                    continue
                if kw.lower() == code.lower() or code.lower().startswith(kw.lower()):
                    code_found = code
                    break
            if code_found:
                break

        # Passe 2 : similarite textuelle sur le libelle
        if not code_found and label_choices:
            norm_label = re.sub(r"\s+", " ", label).strip().lower()
            best, best_score = None, 0.0
            for cand_label, cand_code in label_choices.items():
                if cand_code in used_codes:
                    continue
                score = difflib.SequenceMatcher(
                    None, norm_label, cand_label.strip().lower()
                ).ratio()
                if score > best_score:
                    best, best_score = cand_label, score
            if best is not None and best_score >= 0.35:
                code_found = label_choices[best]

        result[label] = code_found
        if code_found:
            used_codes.add(code_found)

    return result


# --------------------------------------------------------------------------- #
# 2. Recuperation des donnees pour un pays
# --------------------------------------------------------------------------- #

def fetch_country_data(dataset_id, country_code, variable_codes, periods, debug=False, tag=""):
    """POST /dataset/getDataWithoutActivities pour UN pays. Doit etre appele
    pays par pays (contrainte de l'API ONUDI)."""
    url = f"{BASE_URL}/dataset/getDataWithoutActivities"
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
        fname = DEBUG_DIR / f"raw_{tag or country_code}.json"
        fname.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return data


def extract_series(raw, variable_codes, periods):
    """Analyse generique de la reponse de l'API pour en extraire un
    dictionnaire {code_variable: {annee: valeur}}.

    La structure exacte du JSON retourne par getDataWithoutActivities n'est
    pas documentee publiquement dans le detail ; ce parseur parcourt donc
    recursivement la reponse et rassemble tout triplet
    (code_variable, annee, valeur) qu'il reconnait. Si le resultat est vide,
    relancez le script avec --debug et ouvrez le fichier debug/raw_*.json
    pour voir la structure exacte et adapter cette fonction si necessaire.
    """
    var_set = set(variable_codes)
    year_set = set(periods)
    out = {v: {} for v in variable_codes}

    def maybe_record(d: dict):
        # Cherche un code de variable et une periode/valeur dans le meme objet
        code = None
        for k in ("variableCode", "code", "var", "variable"):
            if k in d and d[k] in var_set:
                code = d[k]
                break
        if code is None:
            return
        period = None
        for k in ("period", "year", "periodCode", "time"):
            if k in d:
                p = str(d[k])
                if p in year_set:
                    period = p
                    break
        if period is None:
            return
        value = None
        for k in ("value", "val", "obsValue", "data"):
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
# 3. Construction du classeur Excel
# --------------------------------------------------------------------------- #

HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", name="Arial", size=10)
LABEL_FONT = Font(bold=True, name="Arial", size=10)
CELL_FONT = Font(name="Arial", size=10)
COUNTRY_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")


def write_country_sheet(wb, country_name, indicator_labels, years, series_by_indicator):
    ws = wb.create_sheet(title=country_name[:31])  # 31 = limite Excel
    ws.cell(row=1, column=1, value=f"{country_name} — indicateurs SDG9 / CIP (ONUDI)").font = Font(
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
    ws.column_dimensions["A"].width = 45
    for j in range(2, len(years) + 2):
        ws.column_dimensions[get_column_letter(j)].width = 10

    return ws


def write_comparison_sheet(wb, countries, indicator_labels, years, all_series):
    """Tableau long : une ligne par (Indicateur, Pays), colonnes = annees.
    Trie par indicateur puis par pays pour comparer facilement d'un coup
    d'oeil toutes les valeurs d'un meme indicateur entre pays (via un
    simple filtre Excel sur la colonne Indicateur)."""
    ws = wb.create_sheet(title="Comparaison", index=0)
    ws.cell(row=1, column=1, value="Comparaison entre pays — indicateurs SDG9 / CIP (ONUDI)").font = Font(
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
    ws.column_dimensions["A"].width = 45
    ws.column_dimensions["B"].width = 22
    for j in range(3, len(years) + 3):
        ws.column_dimensions[get_column_letter(j)].width = 10

    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(years) + 2)}{row - 1}"
    return ws


# --------------------------------------------------------------------------- #
# 4. Orchestration
# --------------------------------------------------------------------------- #

def run(discover=False, discover_countries=False, debug=False, output=OUTPUT_FILE):
    print("Connexion au portail ONUDI…")
    meta = get_dataset_metadata()
    dataset_id = meta["id"]
    print(f"  -> dataset '{DATASET_NAME}' id={dataset_id}")

    country_map = build_country_map(meta)

    if discover_countries:
        print("\nPays disponibles dans la base ONUDI :")
        for name in sorted(country_map):
            print(" -", name.title())
        return

    variables = find_variable_list(meta)
    print(f"  -> {len(variables)} variables trouvees dans le jeu de donnees SDG")
    print("  -> Variables detectees (code : libelle) :")
    for v in variables:
        print(f"     - {variable_code(v)!r:<20} : {variable_label(v)!r}")

    if discover:
        return

    if debug:
        DEBUG_DIR.mkdir(exist_ok=True)
        (DEBUG_DIR / "raw_variables.json").write_text(
            json.dumps(variables, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"  -> Liste brute des variables sauvegardee dans {DEBUG_DIR / 'raw_variables.json'}")

    indicator_to_code = match_indicators(variables, INDICATOR_LABELS)
    print("\nCorrespondance indicateur -> code de variable ONUDI :")
    missing = []
    for label, code in indicator_to_code.items():
        status = code if code else "NON TROUVE"
        print(f"  - {label[:60]:<60} -> {status}")
        if not code:
            missing.append(label)
    if missing:
        print(
            "\n[ATTENTION] Certains indicateurs n'ont pas ete reconnus automatiquement.\n"
            "Lancez 'python unido_sdg_scraper.py --discover' pour voir tous les libelles\n"
            "disponibles et ajustez INDICATOR_LABELS si necessaire."
        )

    variable_codes = [c for c in indicator_to_code.values() if c]
    if not variable_codes:
        print("Aucun indicateur reconnu, arret.")
        sys.exit(1)

    wb = Workbook()
    wb.remove(wb.active)  # on retire la feuille par defaut

    all_series = {}  # {pays: {libelle_indicateur: {annee: valeur}}}

    for country in COUNTRIES:
        key = country.lower()
        if key not in country_map:
            print(f"[ATTENTION] Pays introuvable dans la base ONUDI : {country} (ignore)")
            continue
        country_code = country_map[key]
        print(f"Telechargement des donnees pour {country} (code {country_code})…")
        raw = fetch_country_data(
            dataset_id, country_code, variable_codes, YEARS,
            debug=debug, tag=country.replace(" ", "_"),
        )
        by_code = extract_series(raw, variable_codes, YEARS)

        # reindexe par libelle d'indicateur (plus lisible dans le classeur)
        by_label = {}
        for label, code in indicator_to_code.items():
            by_label[label] = by_code.get(code, {}) if code else {}
        all_series[country] = by_label

        write_country_sheet(wb, country, INDICATOR_LABELS, YEARS, by_label)
        time.sleep(0.5)  # courtoisie envers le serveur

    write_comparison_sheet(wb, [c for c in COUNTRIES if c.lower() in country_map],
                            INDICATOR_LABELS, YEARS, all_series)

    wb.save(output)
    print(f"\nTerminee ! Classeur enregistre : {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discover", action="store_true",
                         help="Liste les indicateurs disponibles dans la base SDG de l'ONUDI et quitte")
    parser.add_argument("--discover-countries", action="store_true",
                         help="Liste les pays disponibles dans la base ONUDI et quitte")
    parser.add_argument("--debug", action="store_true",
                         help="Sauvegarde les reponses JSON brutes dans ./debug/ pour inspection")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Nom du fichier Excel de sortie")
    args = parser.parse_args()
    run(discover=args.discover, discover_countries=args.discover_countries,
        debug=args.debug, output=args.output)


if __name__ == "__main__":
    main()

# --------------------------------------------------------------------------- #
# Si vous obtenez une erreur 403 (Cloudflare)
# --------------------------------------------------------------------------- #
#
# La documentation officielle de l'API ONUDI (https://stat.unido.org/unido-
# statistics-portal-api) indique que dans de rares cas Cloudflare bloque les
# clients HTTP simples (requests). Si cela vous arrive :
#
#   pip install undetected-chromedriver selenium
#
# puis remplacez temporairement les appels SESSION.get/SESSION.post par un
# navigateur pilote (voir l'exemple fourni sur la page ci-dessus), ou
# executez simplement le script depuis un reseau/poste different.