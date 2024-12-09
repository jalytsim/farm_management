import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt

# Chemin du fichier GeoTIFF
tif_path = 's3://gfw-data-lake/wri_tropical_tree_cover_extent/v20220922/raster/epsg-4326/10/100000/decile/geotiff/30N_000E.tif'

# Charger le fichier GeoTIFF
with rasterio.open(tif_path) as src:
    # Afficher les métadonnées
    print("Informations du fichier GeoTIFF :")
    print(src.meta)
    
    # Lire les données
    data = src.read(1)  # Lire la première bande
    plt.figure(figsize=(10, 6))
    show(data, cmap="viridis")  # Choisir une colormap (viridis est par défaut)
    plt.title("Affichage du GeoTIFF")
    plt.colorbar(plt.cm.ScalarMappable(cmap="viridis"), label="Valeur des pixels")
    plt.show()
