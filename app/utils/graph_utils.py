from sqlalchemy.orm import sessionmaker
from app.models import Farm, FarmData  # Import your models here
from app import db  # Ensure you have a reference to your database

def get_farm_production_data():
    session = sessionmaker(bind=db.engine)()
    results = session.query(Farm.name, FarmData.quantity).join(FarmData).all()
    session.close()

    # Convert results to a list of dictionaries
    data = [{"name": name, "quantity": quantity} for name, quantity in results]
    return data

def process_farm_data(results):
    farm_names = []
    quantities = []
    
    for item in results:
        farm_names.append(item["name"])
        quantities.append(item["quantity"])

    return farm_names, quantities
