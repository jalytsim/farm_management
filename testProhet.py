"""
test_prophet.py — Test Prophet avec les donnees brutes Sentinel API
Exécuter : python test_prophet.py
Le fichier sentinel_data.json doit etre dans le meme dossier.
"""

import json
import warnings
import pandas as pd
from prophet import Prophet

warnings.filterwarnings('ignore')

# ── Charger le JSON brut Sentinel ────────────────────────────
with open('sentinel_data.json', 'r') as f:
    raw = json.load(f)

# ── Parser le format brut Sentinel → liste propre ─────────────
def parse_sentinel_response(raw_json):
    """
    Transforme la reponse brute Sentinel Statistical API
    en liste de dicts {date, ndvi, savi, evi, nmdi}.
    Extrait uniquement la valeur 'mean' de chaque indice.
    """
    parsed = []
    for item in raw_json['data']:
        date = item['interval']['from'][:10]  # "2020-01-01"
        row  = {'date': date}
        for index_name, index_data in item['outputs'].items():
            if index_name == 'dataMask':
                continue
            mean_val = index_data['bands']['B0']['stats']['mean']
            # Ignorer les valeurs non numeriques (NaN, Infinity)
            try:
                val = float(mean_val)
                if val != val or abs(val) > 1e6:  # NaN ou Infinity
                    val = None
            except (TypeError, ValueError):
                val = None
            row[index_name] = val
        parsed.append(row)
    return parsed

DATA    = parse_sentinel_response(raw)
INDICES = ['ndvi', 'savi', 'evi', 'nmdi']

print(f"\n✅ {len(DATA)} intervalles charges depuis sentinel_data.json")
print(f"   Periode : {DATA[0]['date']} → {DATA[-1]['date']}")

# ── Tiers par indice ──────────────────────────────────────────
def get_tier(index_name, value):
    if value is None:
        return ('N/A', '⬜')
    if index_name in ['ndvi', 'savi', 'evi']:
        if value >= 0.5:  return ('HIGH',   '🟢')
        if value >= 0.3:  return ('MEDIUM', '🟡')
        return                   ('LOW',    '🔴')
    else:  # nmdi
        if value < 0.55:  return ('GOOD',          '🟢')
        if value < 0.70:  return ('MODERATE',       '🟡')
        return                   ('DROUGHT RISK',   '🔴')

# ── Forecast Prophet pour un indice ──────────────────────────
def forecast_index(index_name, periods=4):
    # Filtrer les valeurs nulles
    rows = [(d['date'], d[index_name]) for d in DATA if d.get(index_name) is not None]

    df = pd.DataFrame({
        'ds': pd.to_datetime([r[0] for r in rows]),
        'y':  [r[1] for r in rows]
    })

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='additive',
        interval_width=0.80,
    )
    model.fit(df)

    future   = model.make_future_dataframe(periods=periods, freq='QS')
    forecast = model.predict(future)

    pred = forecast[forecast['ds'] > df['ds'].max()][
        ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
    ].copy()

    return pred

# ── Affichage + sauvegarde ─────────────────────────────────────
print("\n" + "═" * 65)
print("  PROPHET FORECAST — Sentinel-2")
print("  Q2 2025 → Q1 2026  (4 quarters ahead)")
print("═" * 65)

results = {}

for index in INDICES:
    print(f"\n── {index.upper()} ──────────────────────────────────────────────")

    last_val = DATA[-1].get(index)
    last_tier, last_icon = get_tier(index, last_val)
    print(f"  Last known ({DATA[-1]['date']}) : {last_val:.4f}  {last_icon} {last_tier}")
    print(f"  {'Quarter':<12} {'Forecast':>10} {'Low 80%':>10} {'High 80%':>10}  Tier")
    print(f"  {'-'*58}")

    pred = forecast_index(index)
    quarters = []

    for _, row in pred.iterrows():
        q_label = row['ds'].strftime('%Y-Q') + str((row['ds'].month - 1) // 3 + 1)
        val     = round(float(row['yhat']),       4)
        lo      = round(float(row['yhat_lower']), 4)
        hi      = round(float(row['yhat_upper']), 4)
        tier, icon = get_tier(index, val)

        print(f"  {q_label:<12} {val:>10.4f} {lo:>10.4f} {hi:>10.4f}  {icon} {tier}")
        quarters.append({
            "quarter":   q_label,
            "forecast":  val,
            "lower_80":  lo,
            "upper_80":  hi,
            "tier":      tier,
        })

    results[index] = quarters

# ── Sauvegarder les resultats ──────────────────────────────────
with open('sentinel_forecast.json', 'w') as f:
    json.dump({"forecast": results}, f, indent=2)

print("\n" + "═" * 65)
print("  ✅ sentinel_forecast.json saved")
print("═" * 65 + "\n")