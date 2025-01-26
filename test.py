import os
import graphviz
from app import db  # Adjust import as per your app structure
from model import User, District, FarmerGroup, SoilData, Farm, FarmData, Forest, Point, Tree, Weather, Solar, ProduceCategory

def generate_uml():
    # Create a new Graphviz graph
    dot = graphviz.Digraph('UML', filename='uml_diagram.gv')

    # Define nodes for each model
    models = {
        'User': ['id: int', 'username: str', 'email: str', 'password: str', 'phonenumber: str', 'user_type: str', 'is_admin: bool', 'date_created: datetime', 'date_updated: datetime', 'id_start: str'],
        'District': ['id: int', 'name: str', 'region: str', 'date_created: datetime', 'date_updated: datetime', 'modified_by: int', 'created_by: int'],
        'FarmerGroup': ['id: int', 'name: str', 'description: str', 'date_created: datetime', 'date_updated: datetime', 'modified_by: int', 'created_by: int'],
        'SoilData': ['id: int', 'district_id: int', 'internal_id: int', 'device: str', 'owner: str', 'nitrogen: float', 'phosphorus: float', 'potassium: float', 'ph: float', 'temperature: float', 'humidity: float', 'conductivity: float', 'signal_level: float', 'date: date', 'date_created: datetime', 'date_updated: datetime', 'modified_by: int', 'created_by: int'],
        'Farm': ['id: int', 'farm_id: str', 'name: str', 'subcounty: str', 'farmergroup_id: int', 'district_id: int', 'geolocation: str', 'phonenumber: str', 'phonenumber2: str', 'cin: str', 'gender: str', 'date_created: datetime', 'date_updated: datetime', 'modified_by: int', 'created_by: int'],
        'FarmData': ['id: int', 'farm_id: str', 'crop_id: int', 'land_type: str', 'tilled_land_size: float', 'planting_date: date', 'season: int', 'quality: str', 'quantity: int', 'harvest_date: date', 'expected_yield: float', 'actual_yield: float', 'timestamp: datetime', 'channel_partner: str', 'destination_country: str', 'customer_name: str', 'date_created: datetime', 'date_updated: datetime', 'modified_by: int', 'created_by: int', 'number_of_tree: int', 'hs_code: str'],
        'Forest': ['id: int', 'name: str', 'tree_type: str', 'date_created: datetime', 'date_updated: datetime', 'modified_by: int', 'created_by: int'],
        'Point': ['id: int', 'longitude: float', 'latitude: float', 'owner_type: enum', 'owner_id: str', 'district_id: int', 'date_created: datetime', 'date_updated: datetime', 'modified_by: int', 'created_by: int'],
        'Tree': ['id: int', 'forest_id: int', 'point_id: int', 'name: str', 'height: float', 'diameter: float', 'date_planted: date', 'date_cut: date', 'created_by: int', 'modified_by: int', 'date_created: datetime', 'date_updated: datetime', 'type: str'],
        'Weather': ['id: int', 'latitude: float', 'longitude: float', 'timestamp: datetime', 'air_temperature: float', 'humidity: float', 'date_created: datetime', 'date_updated: datetime'],
        'Solar': ['id: int', 'latitude: str', 'longitude: str', 'timestamp: datetime', 'uv_index: float', 'date_created: datetime', 'date_updated: datetime'],
        'ProduceCategory': ['id: int', 'name: str', 'description: str', 'date_created: datetime', 'date_updated: datetime']
    }

    for model_name, attributes in models.items():
        # Create a node for each model
        dot.node(model_name, shape='record', label='{' + f"{model_name}|{'|'.join(attributes)}" + '}')

    # Define relationships (Foreign Key references)
    relationships = [
        ('FarmerGroup', 'Farm'),
        ('District', 'SoilData'),
        ('User', 'District', 'modified_by'),
        ('User', 'District', 'created_by'),
        ('User', 'FarmerGroup', 'modified_by'),
        ('User', 'FarmerGroup', 'created_by'),
        ('User', 'Farm', 'modified_by'),
        ('User', 'Farm', 'created_by'),
        ('User', 'SoilData', 'modified_by'),
        ('User', 'SoilData', 'created_by'),
        ('Farm', 'FarmData'),
        ('District', 'Point'),
        ('User', 'Point', 'modified_by'),
        ('User', 'Point', 'created_by'),
        ('Forest', 'Tree'),
        ('Point', 'Tree'),
        ('Weather', 'Farm'),
        ('Solar', 'Farm')
    ]

    for parent, child, *attr in relationships:
        if attr:
            dot.edge(parent, child, label=f"{attr[0]} FK")
        else:
            dot.edge(parent, child)

    # Save and render the graph
    dot.render('uml_diagram', format='png', cleanup=True)
    print("UML diagram generated and saved as uml_diagram.png")

if __name__ == '__main__':
    generate_uml()
