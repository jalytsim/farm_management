from flask import Blueprint, jsonify
from flask_cors import cross_origin

bp = Blueprint('weather', __name__)

# Données dynamiques pour chaque région
data = {
    "Butambal": {
        "imageUrl": "https://via.placeholder.com/600x400?text=Butambal",
        "farmName": "Ferme de Butambal",
        "temperature": "25.0",
        "humidity": "60.0",
        "solarRadiation": "200.0",
        "windSpeed": "2.0",
        "pressure": "101300",
        "ET0": "5.67",  # Exemple de résultat
        "ETc": "6.80",   # Exemple de résultat
        "latitude": "0.123",
        "longitude": "0.456"
    },
    "Lwengo": {
        "imageUrl": "https://via.placeholder.com/600x400?text=Lwengo",
        "farmName": "Ferme de Lwengo",
        "temperature": "22.5",
        "humidity": "65.0",
        "solarRadiation": "180.0",
        "windSpeed": "1.5",
        "pressure": "100800",
        "ET0": "4.23",  # Exemple de résultat
        "ETc": "5.15",   # Exemple de résultat
        "latitude": "1.123",
        "longitude": "1.456"
    },
    "Mukono": {
        "imageUrl": "https://via.placeholder.com/600x400?text=Mukono",
        "farmName": "Ferme de Mukono",
        "temperature": "24.0",
        "humidity": "55.0",
        "solarRadiation": "210.0",
        "windSpeed": "2.5",
        "pressure": "101500",
        "ET0": "6.12",  # Exemple de résultat
        "ETc": "7.25",   # Exemple de résultat
        "latitude": "2.123",
        "longitude": "2.456"
    }
}

@bp.route('/weather', methods=['GET'])
@cross_origin()  # Permet à toutes les origines de faire des requêtes à cette route
def weather():
    return jsonify(data)
