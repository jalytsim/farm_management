import os
from plantuml import PlantUML, PlantUMLHTTPError
def generate_use_case_diagram(models):
    def sanitize_name(name):
        return name.replace(" ", "_").replace("-", "_")

    uml_code = ["@startuml", "left to right direction"]

    # Ajouter les acteurs à gauche
    left_actors = [actor for actor in models["actors"] if actor != "System"]
    for actor in left_actors:
        uml_code.append(f"actor {sanitize_name(actor)}")

    # Ajouter le système à droite
    uml_code.append(f"actor {sanitize_name('System')} as System")

    # Ajouter le rectangle pour les cas d'utilisation
    uml_code.append("rectangle System {")
    
    # Ajouter les cas d'utilisation au centre
    use_cases = set(uc["use_case"] for uc in models["use_cases"])
    for use_case in use_cases:
        uml_code.append(f"    usecase \"{use_case}\" as UC_{sanitize_name(use_case)}")

    uml_code.append("}")

    # Ajouter les relations
    for relation in models["use_cases"]:
        actor = sanitize_name(relation["actor"])
        use_case = sanitize_name(relation["use_case"])
        uml_code.append(f"{actor} --> UC_{use_case}")

    # Ajouter les relations include et extend
    for relation in models.get("relations", []):
        rel_type = relation["type"]
        from_case = sanitize_name(relation["from"])
        to_case = sanitize_name(relation["to"])
        if rel_type == "include":
            uml_code.append(f"UC_{from_case} ..> UC_{to_case} : include")
        elif rel_type == "extend":
            uml_code.append(f"UC_{from_case} .> UC_{to_case} : extend")

    uml_code.append("@enduml")
    uml_content = "\n".join(uml_code)

    # Afficher le contenu UML pour debugging
    print("Contenu UML genere :")
    print(uml_content)

    # Sauvegarder le fichier
    output_file = "use_case_diagram.puml"
    with open(output_file, "w") as file:
        file.write(uml_content)

    # Generer le diagramme
    try:
        plantuml_server = PlantUML(url="http://www.plantuml.com/plantuml/img/")
        diagram_output = output_file.replace(".puml", ".png")
        plantuml_server.processes_file(output_file, outfile=diagram_output)
        print(f"Diagramme d'utilisation UML genere : {diagram_output}")
    except PlantUMLHTTPError as e:
        print("Erreur avec le serveur PlantUML :", e)



def generate_class_diagram(models):
    """
    Genère un diagramme de classes UML base sur les modèles donnes.
    
    Args:
        models (dict): Dictionnaire contenant les classes et leurs relations.
    """
    uml_code = ["@startuml"]

    # Ajouter les classes
    for class_name, details in models["classes"].items():
        uml_code.append(f"class {class_name} {{")
        for attribute in details["attributes"]:
            uml_code.append(f"    {attribute}")
        uml_code.append("}")

    # Ajouter les relations
    for relation in models["relations"]:
        uml_code.append(f"{relation['from']} --> {relation['to']} : {relation.get('label', '')}")

    uml_code.append("@enduml")
    uml_content = "\n".join(uml_code)

    # Sauvegarder le diagramme dans un fichier
    output_file = "class_diagram.puml"
    with open(output_file, "w") as file:
        file.write(uml_content)

    # Generer le fichier image avec PlantUML
    plantuml_server = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    diagram_output = output_file.replace(".puml", ".png")
    plantuml_server.processes_file(output_file, outfile=diagram_output)

    print(f"Diagramme de classes UML genere: {diagram_output}")


def generate_sequence_diagram(case_name, interactions, components=None):
    """
    Génère un diagramme de séquence UML pour un cas d'utilisation donné avec des interactions détaillées.

    Args:
        case_name (str): Nom du cas d'utilisation.
        interactions (list): Liste des interactions sous forme de tuples (source, destination, action).
        components (list): Liste supplémentaire de composants ou acteurs à inclure dans le diagramme.
    """
    uml_code = ["@startuml"]
    uml_code.append(f"title Diagramme de séquence pour {case_name}")

    # Définir les acteurs et composants uniques
    all_components = set(source for source, _, _ in interactions) | set(destination for _, destination, _ in interactions)
    if components:
        all_components.update(components)

    for component in sorted(all_components):
        if "Admin" in component or "Client" in component or "GFW" in component:
            uml_code.append(f"actor {component}")
        elif "Écran" in component or "Interface" in component:
            uml_code.append(f"boundary {component}")
        elif "Base de données" in component or "Système" in component:
            uml_code.append(f"database {component}")
        else:
            uml_code.append(f"participant {component}")

    # Ajouter les interactions
    for source, destination, action in interactions:
        uml_code.append(f"{source} -> {destination}: {action}")

    uml_code.append("@enduml")
    uml_content = "\n".join(uml_code)

    # Sauvegarde du fichier PlantUML
    output_file = f"sequence_diagram_{case_name.replace(' ', '_').lower()}.puml"
    with open(output_file, "w") as file:
        file.write(uml_content)

    print(f"Diagramme de séquence UML généré: {output_file}")


def generate_detailed_sequence_diagram(case_name, interactions):
    """
    Génère un diagramme de séquence UML détaillé avec des types spécifiques de participants.
    
    Args:
        case_name (str): Nom du cas d'utilisation.
        interactions (list): Liste des interactions sous forme de tuples (source, destination, action).
    """
    try:
        uml_code = ["@startuml"]
        uml_code.append(f"title Diagramme de séquence pour {case_name}")
        
        # Définition des types de participants
        uml_code.append("actor Client")
        uml_code.append("boundary Ecran_Utilisateur")
        uml_code.append("control Controlleur")
        uml_code.append("entity Service_Utilisateur")
        uml_code.append("database Base_de_donnees")
        uml_code.append("collections Cache_Systeme")
        uml_code.append("queue Queue_Operations")
        uml_code.append("entity Système_Externe")
        
        # Ajout des interactions
        for interaction in interactions:
            source, destination, action = interaction
            uml_code.append(f"{source} -> {destination}: {action}")
        
        uml_code.append("@enduml")
        uml_content = "\n".join(uml_code)

        # Sauvegarde du fichier PlantUML
        output_file = f"sequence_diagram_{case_name.replace(' ', '_')}.puml"
        with open(output_file, "w") as file:
            file.write(uml_content)
        print(f"Fichier PlantUML généré: {output_file}")
        
        # Génération du fichier image avec PlantUML
        plantuml_server = PlantUML(url="http://www.plantuml.com/plantuml/img/")
        diagram_output = output_file.replace(".puml", ".png")
        plantuml_server.processes_file(output_file, outfile=diagram_output)
        
        print(f"Diagramme de séquence UML généré: {diagram_output}")
    
    except Exception as e:
        print(f"Erreur lors de la génération du diagramme: {e}")

def generate_package_diagram(packages):
    """
    Genère un diagramme de paquetage UML.
    
    Args:
        packages (dict): Dictionnaire contenant les paquetages et leurs dependances.
    """
    uml_code = ["@startuml"]
    uml_code.append("package Système {")
    
    # Ajout des paquetages et des dependances
    for package, sub_packages in packages.items():
        uml_code.append(f"package {package} {{")
        for sub_package in sub_packages:
            uml_code.append(f"    class {sub_package}")
        uml_code.append("}")

    uml_code.append("}")
    uml_code.append("@enduml")

    uml_content = "\n".join(uml_code)

    # Sauvegarde et generation
    output_file = "package_diagram.puml"
    with open(output_file, "w") as file:
        file.write(uml_content)

    plantuml_server = PlantUML(url="http://www.plantuml.com/plantuml")
    diagram_output = output_file.replace(".puml", ".png")
    
    # Ajout de la gestion des exceptions
    try:
        plantuml_server.processes_file(output_file, outfile=diagram_output)
        print(f"Diagramme de paquetage UML genere: {diagram_output}")
    except Exception as e:
        print(f"Erreur lors de la generation de l'image: {e}")




def generate_deployment_diagram(components):
    """
    Genère un diagramme de deploiement UML.
    
    Args:
        components (list): Liste des composants et des relations sous forme de tuples (source, destination, relation).
    """
    uml_code = ["@startuml"]
    uml_code.append("node Serveur_Web {")
    uml_code.append("  [Application]")

    # Ajout des composants externes
    uml_code.append("}")
    uml_code.append("database Serveur_BDD {")
    uml_code.append("  [Base de Donnees]")
    uml_code.append("}")

    # Ajout des relations
    for component in components:
        source, destination, relation = component
        uml_code.append(f"{source} --> {destination}: {relation}")

    uml_code.append("@enduml")

    uml_content = "\n".join(uml_code)

    # Sauvegarde et generation
    output_file = "deployment_diagram.puml"
    with open(output_file, "w") as file:
        file.write(uml_content)

    plantuml_server = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    diagram_output = output_file.replace(".puml", ".png")
    plantuml_server.processes_file(output_file, outfile=diagram_output)

    print(f"Diagramme de deploiement UML genere: {diagram_output}")

# Exemple
# generate_deployment_diagram([
#     ("Serveur_Web", "Serveur_BDD", "Requêtes SQL"),
#     ("Utilisateur", "Serveur_Web", "HTTP Request")
# ])


# Exemple
# generate_package_diagram({
#     "Module Authentification": ["Login", "Inscription"],
#     "Module Gestion": ["Utilisateur", "Admin", "Produit"]
# })


# generate_sequence_diagram("Farm Management", [
#     ("Admin", "Système", "Acceder à la gestion des fermes"),
#     ("Système", "Admin", "Afficher la liste des fermes"),
#     ("Admin", "Système", "Ajouter Modifier Supprimer une ferme"),
#     ("Système", "Admin", "Confirmer l'operation")
# ])


# generate_sequence_diagram("Admin View All Farms", [
#     ("Admin", "Système", "Demander la liste de toutes les fermes"),
#     ("Système", "Admin", "Retourner la liste de toutes les fermes")
# ])

# generate_sequence_diagram("Create Account", [
#     ("Admin", "Système", "Remplir le formulaire de creation de compte"),
#     ("Système", "Admin", "Valider les informations"),
#     ("Admin", "Système", "Soumettre le formulaire"),
#     ("Système", "Admin", "Confirmer la creation du compte")
# ])

# generate_sequence_diagram("Polygon Creation", [
#     ("Admin_Client", "Système", "Demarrer la creation du polygone"),
#     ("Système", "Admin_Client", "Afficher l'interface de dessin"),
#     ("Admin_Client", "Système", "Dessiner le polygone"),
#     ("Admin_Client", "Système", "Valider le polygone"),
#     ("Système", "Admin_Client", "Enregistrer le polygone")
# ])

# generate_sequence_diagram("Import Farm Data", [
#     ("Admin_Client", "Système", "Telecharger le fichier CSV"),
#     ("Système", "Admin_Client", "Valider le fichier"),
#     ("Admin_Client", "Système", "Soumettre l'importation"),
#     ("Système", "Admin_Client", "Confirmer l'importation des donnees")
# ])

# generate_sequence_diagram("Crop Management", [
#     ("Admin_Client", "Système", "Acceder à la gestion des cultures"),
#     ("Système", "Admin_Client", "Afficher les cultures existantes"),
#     ("Admin_Client", "Système", "Ajouter Modifier Supprimer une culture"),
#     ("Système", "Admin_Client", "Confirmer l'operation")
# ])

# generate_sequence_diagram("View All Farms", [
#     ("Client", "Système", "Demander à voir toutes les fermes"),
#     ("Système", "Client", "Retourner la liste des fermes")
# ])

# generate_sequence_diagram("Generate Farm Report", [
#     ("GFW", "Système", "Demander un rapport de ferme"),
#     ("Système", "GFW", "Generer le rapport base sur les donnees"),
#     ("Système", "GFW", "Fournir le rapport de ferme")
# ])

# generate_sequence_diagram("Generate Carbon Report", [
#     ("GFW", "Système", "Demander un rapport de carbone"),
#     ("Système", "GFW", "Generer le rapport de carbone base sur les donnees"),
#     ("Système", "GFW", "Fournir le rapport de carbone")
# ])

# generate_sequence_diagram("Provide Environmental Data", [
#     ("GFW", "Système", "Demander des donnees environnementales"),
#     ("Système", "GFW", "Fournir les donnees environnementales demandees")
# ])

# generate_sequence_diagram("Provide Account List", [
#     ("GFW", "Système", "Demander la liste des comptes"),
#     ("Système", "GFW", "Retourner la liste des comptes")
# ])

# Rechercher une localisation geographique
# generate_sequence_diagram("Rechercher une localisation geographique", [
#     ("Utilisateur", "Systeme", "Entrer les coordonnees ou le nom de la localisation"),
#     ("Systeme", "API_Cartographique", "Envoyer une requête de recherche"),
#     ("API_Cartographique", "Systeme", "Retourner les details de la localisation"),
#     ("Systeme", "Utilisateur", "Afficher les resultats de recherche")
# ])

# # Obtenir les informations meteorologiques associees à la localisation recherchee
# generate_sequence_diagram("Obtenir les informations meteorologiques", [
#     ("Utilisateur", "Systeme", "Selectionner une localisation"),
#     ("Systeme", "API_Meteorologique", "Demander les donnees meteorologiques"),
#     ("API_Meteorologique", "Systeme", "Retourner les donnees meteorologiques"),
#     ("Systeme", "Utilisateur", "Afficher les informations meteorologiques")
# ])

# # Afficher les graphiques meteorologiques pour la localisation selectionnee
# generate_sequence_diagram("Afficher les graphiques meteorologiques", [
#     ("Utilisateur", "Systeme", "Demander des graphiques pour la localisation"),
#     ("Systeme", "API_Meteorologique", "Recuperer les donnees necessaires"),
#     ("API_Meteorologique", "Systeme", "Retourner les donnees meteorologiques"),
#     ("Systeme", "Utilisateur", "Afficher les graphiques meteorologiques")
# ])

# # Consulter les previsions meteorologiques des jours à venir
# generate_sequence_diagram("Consulter les previsions meteorologiques", [
#     ("Utilisateur", "Systeme", "Entrer les coordonnees ou la localisation"),
#     ("Systeme", "API_Meteorologique", "Recuperer les previsions pour les jours à venir"),
#     ("API_Meteorologique", "Systeme", "Retourner les previsions meteorologiques"),
#     ("Systeme", "Utilisateur", "Afficher les previsions")
# ])

# # Calculer les valeurs d'ET₀ et d'Etc
# generate_sequence_diagram("Calculer les valeurs ET0 et ETc", [
#     ("Utilisateur", "Systeme", "Selectionner une localisation et une culture"),
#     ("Systeme", "Base_de_donnees", "Recuperer les coefficients Kc"),
#     ("Systeme", "API_Meteorologique", "Recuperer les donnees climatiques"),
#     ("Systeme", "Systeme", "Calculer ET0 et ETc"),
#     ("Systeme", "Utilisateur", "Afficher les valeurs d'ET0 et d'ETc")
# ])

# # Afficher les indices thermiques (GDD, HDD, CDD)
# generate_sequence_diagram("Afficher les indices thermiques", [
#     ("Utilisateur", "Systeme", "Selectionner une localisation"),
#     ("Systeme", "API_Meteorologique", "Recuperer les donnees climatiques"),
#     ("Systeme", "Systeme", "Calculer GDD, HDD et CDD"),
#     ("Systeme", "Utilisateur", "Afficher les indices thermiques")
# ])

# # Fournir les donnees meteorologiques necessaires pour les fonctionnalites
# generate_sequence_diagram("Fournir les donnees meteorologiques necessaires", [
#     ("Systeme", "API_Meteorologique", "Envoyer une requete pour les donnees climatiques"),
#     ("API_Meteorologique", "Systeme", "Retourner les donnees meteorologiques"),
#     ("Systeme", "Base_de_donnees", "Stocker ou mettre en cache les donnees utiles"),
#     ("Systeme", "Modules_Fonctionnels", "Fournir les donnees necessaires")
# ])

# # Gerer les utilisateurs par l'admin
# generate_sequence_diagram("Gerer les utilisateurs par l'admin", [
#     ("Admin", "Systeme", "Creer, lire, modifier ou supprimer un utilisateur"),
#     ("Systeme", "Base_de_donnees", "Enregistrer ou mettre à jour les informations utilisateur"),
#     ("Base_de_donnees", "Systeme", "Retourner la confirmation de l'operation"),
#     ("Systeme", "Admin", "Afficher les resultats de la gestion")
# ])

# Exemple de modèle pour le diagramme d'utilisation
use_case_models = {
    "actors": ["Admin", "Client", "System"],
    "use_cases": [
        {"actor": "Admin", "use_case": "Farm Management"},
        {"actor": "Admin", "use_case": "Admin View All Farms"},        
        {"actor": "Admin", "use_case": "Create Account"},
        {"actor": "Admin", "use_case": "Polygon Creation"},
        {"actor": "Admin", "use_case": "Import Farm Data"},
        {"actor": "Admin", "use_case": "Crop Management"},
        {"actor": "Client", "use_case": "Farm Management"},
        {"actor": "Client", "use_case": "Polygon Creation"},
        {"actor": "Client", "use_case": "Import Farm Data"},
        {"actor": "Client", "use_case": "Crop Management"},
        {"actor": "Client", "use_case": "View All Farms"},
        {"actor": "GFW", "use_case": "Generate Farm Report"},
        {"actor": "GFW", "use_case": "Generate Carbon Report"},
        {"actor": "GFW", "use_case": "Provide Environmental Data"},
        {"actor": "GFW", "use_case": "Provide Account List"}  # Added since it's now mentioned
    ],
    "relations": [
        # Include relationships
        {"type": "include", "from": "Farm Management", "to": "Polygon Creation"},
        {"type": "include", "from": "Farm Management", "to": "Import Farm Data"},
        {"type": "include", "from": "Crop Management", "to": "Import Farm Data"},

        # Extend relationships
        {"type": "extend", "from": "View All Farms", "to": "Provide Farm Data"},
        {"type": "extend", "from": "Create Account", "to": "Provide Account List"},
        {"type": "extend", "from": "Farm Management", "to": "Generate Farm Report"},
        {"type": "extend", "from": "Farm Management", "to": "Generate Carbon Report"},
    ]
}



# Exemple de modèle pour le diagramme de classes
class_models = {
    "classes": {
        "User": {
            "attributes": [
                "id: Integer",
                "username: String",
                "email: String",
                "password: String",
                "phonenumber: String",
                "user_type: String",
                "is_admin: Boolean",
                "date_created: DateTime",
                "date_updated: DateTime",
                "id_start: String"
            ],
             "methods": [
                "create_account()",
                "provide_account_list()",
                "admin_view_all_farms()"
            ]
        },
        "District": {
            "attributes": [
                "id: Integer",
                "name: String",
                "region: String",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer",
                "created_by: Integer"
            ]
        },
        "FarmerGroup": {
            "attributes": [
                "id: Integer",
                "name: String",
                "description: Text",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer",
                "created_by: Integer"
            ]
        },
        "SoilData": {
            "attributes": [
                "id: Integer",
                "district_id: Integer",
                "internal_id: Integer",
                "device: String",
                "owner: String",
                "nitrogen: Float",
                "phosphorus: Float",
                "potassium: Float",
                "ph: Float",
                "temperature: Float",
                "humidity: Float",
                "conductivity: Float",
                "signal_level: Float",
                "date: Date",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer",
                "created_by: Integer"
            ]
        },
        "Farm": {
            "attributes": [
                "id: Integer",
                "farm_id: String",
                "name: String",
                "subcounty: String",
                "farmergroup_id: Integer",
                "district_id: Integer",
                "geolocation: String",
                "phonenumber: String",
                "phonenumber2: String",
                "cin: String",
                "gender: String",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer",
                "created_by: Integer"
            ],
            "methods": [
                "view_all_farms()",
                "generate_farm_report()",
                "import_farm_data()"
            ]
        },
        "FarmData": {
            "attributes": [
                "id: Integer",
                "farm_id: String",
                "crop_id: Integer",
                "land_type: String",
                "tilled_land_size: Float",
                "planting_date: Date",
                "season: Integer",
                "quality: String",
                "quantity: Integer",
                "harvest_date: Date",
                "expected_yield: Float",
                "actual_yield: Float",
                "timestamp: DateTime",
                "channel_partner: String",
                "destination_country: String",
                "customer_name: String",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer",
                "created_by: Integer",
                "number_of_tree: Integer",
                "hs_code: String"
            ],
            "methods": [
                "generate_farm_report()"
            ]
        },
        "Forest": {
            "attributes": [
                "id: Integer",
                "name: String",
                "tree_type: String",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer",
                "created_by: Integer"
            ]
        },
        "Point": {
            "attributes": [
                "id: Integer",
                "longitude: Float",
                "latitude: Float",
                "owner_type: Enum(forest, farmer, tree)",
                "owner_id: String",
                "district_id: Integer",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer",
                "created_by: Integer"
            ]
        },
        "Tree": {
            "attributes": [
                "id: Integer",
                "forest_id: Integer",
                "point_id: Integer",
                "name: String",
                "height: Float",
                "diameter: Float",
                "date_planted: Date",
                "date_cut: Date",
                "created_by: Integer",
                "modified_by: Integer",
                "date_created: DateTime",
                "date_updated: DateTime",
                "type: String"
            ]
        },
        "Weather": {
            "attributes": [
                "id: Integer",
                "latitude: Float",
                "longitude: Float",
                "timestamp: DateTime",
                "air_temperature: Float",
                "air_temperature_80m: Float",
                "air_temperature_100m: Float",
                "air_temperature_1000hpa: Float",
                "air_temperature_800hpa: Float",
                "air_temperature_500hpa: Float",
                "air_temperature_200hpa: Float",
                "pressure: Float",
                "cloud_cover: Float",
                "current_direction: Float",
                "current_speed: Float",
                "gust: Float",
                "humidity: Float",
                "ice_cover: Float",
                "precipitation: Float",
                "snow_depth: Float",
                "sea_level: Float",
                "swell_direction: Float",
                "swell_height: Float",
                "swell_period: Float",
                "secondary_swell_direction: Float",
                "secondary_swell_height: Float",
                "secondary_swell_period: Float",
                "visibility: Float",
                "water_temperature: Float"
            ]
        },
        "Solar": {
            "attributes": [
                "id: Integer",
                "latitude: String(20)",
                "longitude: String(20)",
                "timestamp: DateTime",
                "uv_index: Float",
                "downward_short_wave_radiation_flux: Float",
                "source: String(100)",
                "start_time: DateTime",
                "end_time: DateTime",
                "date_created: DateTime",
                "date_updated: DateTime"
            ]
        },
        "ProduceCategory": {
            "attributes": [
                "id: Integer",
                "name: String(255)",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer (ForeignKey to User)",
                "created_by: Integer (ForeignKey to User)"
            ]
        },
        "Crop": {
            "attributes": [
                "id: Integer",
                "name: String(255)",
                "weight: Float",
                "category_id: Integer (ForeignKey to ProduceCategory)",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer (ForeignKey to User)",
                "created_by: Integer (ForeignKey to User)"
            ],
            "methods": [
                "crop_management()",
                "generate_carbon_report()"
            ]
        },
        "Grade": {
            "attributes": [
                "id: Integer",
                "crop_id: Integer (ForeignKey to Crop)",
                "grade_value: String(50)",
                "description: Text",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer (ForeignKey to User)",
                "created_by: Integer (ForeignKey to User)"
            ]
        },
        "CropCoefficient": {
            "attributes": [
                "id: Integer",
                "crop_id: Integer (ForeignKey to Crop)",
                "stage: String(50)",
                "kc_value: Float",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer (ForeignKey to User)",
                "created_by: Integer (ForeignKey to User)"
            ]
        },
        "Irrigation": {
            "attributes": [
                "id: Integer",
                "crop_id: Integer (ForeignKey to Crop)",
                "farm_id: Integer (ForeignKey to Farm)",
                "irrigation_date: Date",
                "water_applied: Float",
                "method: String(100)",
                "date_created: DateTime",
                "date_updated: DateTime",
                "modified_by: Integer (ForeignKey to User)",
                "created_by: Integer (ForeignKey to User)"
            ]
        },
        "Pays": {
            "attributes": [
                "id: SmallInteger",
                "code: Integer",
                "alpha2: String(2)",
                "alpha3: String(3)",
                "nom_en_gb: String(45)",
                "nom_fr_fr: String(45)"
            ]
        }
    },
    "relations": [
        {"from": "User", "to": "District", "label": "created"},
        {"from": "User", "to": "FarmerGroup", "label": "created"},
        {"from": "User", "to": "SoilData", "label": "created"},
        {"from": "User", "to": "Farm", "label": "created"},
        {"from": "User", "to": "FarmData", "label": "created"},
        {"from": "User", "to": "Forest", "label": "created"},
        {"from": "User", "to": "Point", "label": "created"},
        {"from": "User", "to": "Tree", "label": "created"},
        {"from": "User", "to": "Weather", "label": "created"},
        {"from": "User", "to": "Crop", "label": "created"},
        {"from": "User", "to": "ProduceCategory", "label": "created"},
        {"from": "User", "to": "Grade", "label": "created"},
        {"from": "User", "to": "CropCoefficient", "label": "created"},
        {"from": "User", "to": "Irrigation", "label": "created"},
        {"from": "User", "to": "Solar", "label": "created"},
        {"from": "User", "to": "Pays", "label": "created"},
        {"from": "District", "to": "SoilData", "label": "has"},
        {"from": "District", "to": "Farm", "label": "has"},
        {"from": "FarmerGroup", "to": "Farm", "label": "has"},
        {"from": "Farm", "to": "FarmData", "label": "has"},
        {"from": "Forest", "to": "Tree", "label": "has"},
        {"from": "Point", "to": "Tree", "label": "has"},
        {"from": "Crop", "to": "Grade", "label": "has"},
        {"from": "Crop", "to": "CropCoefficient", "label": "has"},
        {"from": "Crop", "to": "Irrigation", "label": "has"},
        {"from": "Crop", "to": "Weather", "label": "has"},
        {"from": "Crop", "to": "Solar", "label": "has"},
        {"from": "ProduceCategory", "to": "Crop", "label": "has"}
    ]
}

# Generer les diagrammes
# generate_use_case_diagram(use_case_models)
generate_class_diagram(class_models)
