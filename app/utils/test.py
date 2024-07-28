from shapely.geometry import Polygon
from pyproj import Transformer

# Coordonnées géographiques (latitude, longitude)
coordinates = [
    (0.54519, 32.588851),
    (0.545424, 32.588883),
    (0.545861, 32.58914),
    (0.545409, 32.590049),
    (0.545245, 32.590066),
    (0.545663, 32.590386),
    (0.545458, 32.590741),
    (0.545196, 32.590601),
    (0.54479, 32.591077),
    (0.544532, 32.591221),
    (0.544332, 32.591223),
    (0.54422, 32.591454),
    (0.543855, 32.59116),
    (0.543857, 32.591492),
    (0.543428, 32.591973),
    (0.542925, 32.591661),
    (0.542902, 32.591228),
    (0.542433, 32.590995),
    (0.54519, 32.588851)
]

# Convertir les coordonnées (latitude, longitude) en coordonnées projetées (x, y)
transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
projected_coords = [transformer.transform(lon, lat) for lat, lon in coordinates]

# Créer un polygone avec les coordonnées projetées
projected_polygon = Polygon(projected_coords)

# Calculer l'aire en mètres carrés
area = projected_polygon.area
print(f"L'aire du polygone est de {area:.2f} mètres carrés")
