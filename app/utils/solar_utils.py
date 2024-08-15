import json
from datetime import datetime
from app.models import Solar
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
    try:
        db.session.add(new_solar)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating solar data: {e}")
    finally:
        db.session.close()

def update_solar(id, **kwargs):
    solar = Solar.query.get(id)
    if solar:
        for key, value in kwargs.items():
            if hasattr(solar, key):
                setattr(solar, key, value)
        solar.date_updated = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error updating solar data: {e}")
        finally:
            db.session.close()

def delete_solar(id):
    solar = Solar.query.get(id)
    if solar:
        try:
            db.session.delete(solar)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting solar data: {e}")
        finally:
            db.session.close()

def get_all_solar_data():
    try:
        return Solar.query.all()
    except Exception as e:
        print(f"Error fetching solar data: {e}")
        return []

def insert_solar_data_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    insert_solar_data(data)

def insert_solar_data(data):
    latitude = data.get('meta', {}).get('lat')
    longitude = data.get('meta', {}).get('lng')

    for hour in data.get('hours', []):
        timestamp = datetime.fromisoformat(hour['time'].replace('Z', '+00:00'))
        uv_index = hour.get('uvIndex', {}).get('noaa')
        downward_short_wave_radiation_flux = hour.get('downwardShortWaveRadiationFlux', {}).get('noaa')

        create_solar(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            uv_index=uv_index,
            downward_short_wave_radiation_flux=downward_short_wave_radiation_flux
        )

def get_solar_data(latitude, longitude, timestamp):
    try:
        result = db.session.query(
            Solar.downward_short_wave_radiation_flux,
            Solar.latitude,
            Solar.longitude
        ).filter(
            Solar.latitude == latitude,
            Solar.longitude == longitude,
            Solar.timestamp == timestamp
        ).first()

        if result:
            return {
                'downward_short_wave_radiation_flux': result.downward_short_wave_radiation_flux
            }
        else:
            print("No result found")
            return None
    except Exception as e:
        print(f"Error querying solar data: {e}")
        return None
