import json
from app.models import Solar
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app import db

def create_solar(latitude, longitude, timestamp, uv_index=None, downward_short_wave_radiation_flux=None,
                  source=None, start_time=None, end_time=None):
    new_solar = Solar(
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp,
        uv_index=uv_index,
        downward_short_wave_radiation_flux=downward_short_wave_radiation_flux,
        source=source,
        start_time=start_time,
        end_time=end_time,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(new_solar)
    db.session.commit()

def update_solar(id, **kwargs):
    solar = Solar.query.get(id)
    if solar:
        for key, value in kwargs.items():
            if hasattr(solar, key):
                setattr(solar, key, value)
        solar.date_updated = datetime.utcnow()
        db.session.commit()

def delete_solar(id):
    solar = Solar.query.get(id)
    if solar:
        db.session.delete(solar)
        db.session.commit()

def get_all_solar_data():
    return Solar.query.all()

def insert_solar_data_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    latitude = data['meta']['lat']
    longitude = data['meta']['lng']
    
    for hour in data['hours']:
        print(f"Processing hour data: {hour}")  # Affiche les données pour le débogage
        
        timestamp = datetime.fromisoformat(hour['time'].replace('Z', '+00:00'))
        
        # Vérifiez la présence des clés et imprimez les valeurs si elles existent
        uv_index = hour.get('uvIndex', {}).get('noaa', None)
        downward_short_wave_radiation_flux = hour.get('downwardShortWaveRadiationFlux', {}).get('noaa', None)

        # Impression des valeurs pour vérifier ce qui est extrait
        print(f"UV Index: {uv_index}, Downward Short Wave Radiation Flux: {downward_short_wave_radiation_flux}")
        
        create_solar(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            uv_index=uv_index,
            downward_short_wave_radiation_flux=downward_short_wave_radiation_flux
        )

def get_solar_data(latitude, longitude, timestamp):
    # Créer une session
    session = sessionmaker(bind=db.engine)()

    # Impression pour le débogage
    print(f"Querying with latitude: {latitude}, longitude: {longitude}, timestamp: {timestamp}")

    # Effectuer la requête
    result = session.query(
        Solar.downward_short_wave_radiation_flux,
        Solar.latitude,
        Solar.longitude
    ).filter(
        Solar.latitude == latitude,
        Solar.longitude == longitude,

        Solar.timestamp == timestamp
    ).first()

    # Fermer la session
    session.close()

    # Impression pour le débogage
    if result:
        print(f"Found result: {result}")
        return {
            'downward_short_wave_radiation_flux': result.downward_short_wave_radiation_flux
        }
    else:
        print("No result found")
        return None