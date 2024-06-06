    // Créer la carte Leaflet
    var map = L.map('map').setView([0, 0], 2); // Ajustez les coordonnées et le niveau de zoom selon vos besoins

    // Ajouter une couche de tuiles (carte de fond)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Charger le fichier GeoJSON et ajouter à la carte
    fetch('geoBoundaries-UGA-ADM3.geojson')
        .then(response => response.json())
        .then(data => {
            // Créer une couche GeoJSON et ajouter à la carte
            L.geoJSON(data).addTo(map);
        });
