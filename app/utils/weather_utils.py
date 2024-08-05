from app.models import Forest
from datetime import datetime
from flask_login import current_user
import numpy as np
from app import db

def calculate_penman_et0(T, RH, Rs, u2, P):
    # Saturation vapor pressure (es) in kPa
    es = 0.6108 * np.exp((17.27 * T) / (T + 237.3))
    
    # Actual vapor pressure (ea) in kPa
    ea = (RH / 100) * es
    
    # Slope of the saturation vapor pressure curve (Δ) in kPa/°C
    delta = (4098 * es) / ((T + 237.3)**2)
    
    # Psychrometric constant (γ) in kPa/°C
    gamma = (0.001013 * P) / (0.622 * 2.45)
    
    # Convert radiation from W/m² to MJ/m²/day
    Rn = Rs * 86.4 * 10**-3  # Net radiation (Rn) in MJ/m²/day
    
    # Soil heat flux density (G) in MJ/m²/day (assumed to be negligible)
    G = 0
    
    # Penman ET₀ calculation in mm/day
    ET0 = ((delta * (Rn - G)) + (gamma * (900 / (T + 273)) * u2 * (es - ea))) / (delta + gamma * (1 + 0.34 * u2))
    
    return ET0

# Exemple de données pour Wakiso, Kyenjojo, Butambala, Mukono
# T = 25.0    # Température en °C
# RH = 60.0   # Humidité relative en %
# Rs = 200.0  # Radiation solaire en W/m² (Downward Short-Wave Radiation Flux)
# u2 = 2.0    # Vitesse du vent en m/s
# P = 101300  # Pression atmosphérique en Pa

# et0 = calculate_penman_et0(T, RH, Rs, u2, P)
# print(f"ET₀ : {et0:.2f} mm/jour")



# Calcul pour ETc
def calculate_blaney_criddle_etc(T_moy, Kc):
    # Calcul du facteur de température (P)
    P = 0.46 * T_moy + 8.13
    
    # Calcul de l'ETc
    ETc = P * Kc
    
    return ETc

# Exemple de données
# T_moy = 25.0  # Température moyenne en °C
# Kc = 1.2      # Coefficient de culture

# et_c = calculate_blaney_criddle_etc(T_moy, Kc)
# print(f"ETc : {et_c:.2f} mm/jour")


def create_forest(name, tree_type):
    new_forest = Forest(
        name=name,
        tree_type=tree_type,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow(),
        created_by=current_user.id,
        modified_by=current_user.id
    )
    db.session.add(new_forest)
    db.session.commit()

def update_forest(id, name, tree_type):
    forest = db.session.query(Forest).get(id)
    if forest:
        forest.name = name
        forest.tree_type = tree_type
        forest.date_updated = datetime.utcnow()
        forest.modified_by = current_user.id
        db.session.commit()

def delete_forest(id):
    forest = db.session.query(Forest).get(id)
    if forest:
        db.session.delete(forest)
        db.session.commit()
        
def get_all_forests():
    return db.session.query(Forest).all()

