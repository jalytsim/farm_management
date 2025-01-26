from plantuml import PlantUML

def generate_package_diagram(packages, relations=None):
    """
    Génère un diagramme de paquetage UML avec relations.
    
    Args:
        packages (dict): Dictionnaire contenant les paquetages et leurs classes.
        relations (list): Liste des relations entre classes ou paquetages.
    """
    uml_code = ["@startuml"]
    uml_code.append("package Système {")
    
    # Ajout des paquetages et des classes
    for package, sub_packages in packages.items():
        uml_code.append(f"package {package} {{")
        for sub_package in sub_packages:
            uml_code.append(f"    class {sub_package}")
        uml_code.append("}")

    uml_code.append("}")
    
    # Ajout des relations si elles existent
    if relations:
        for relation in relations:
            uml_code.append(relation)

    uml_code.append("@enduml")

    uml_content = "\n".join(uml_code)

    # Sauvegarde du fichier UML
    output_file = "package_diagram_with_relations.puml"
    with open(output_file, "w") as file:
        file.write(uml_content)

    plantuml_server = PlantUML(url="http://www.plantuml.com/plantuml")
    diagram_output = output_file.replace(".puml", ".png")
    
    # Génération avec gestion des exceptions
    try:
        plantuml_server.processes_file(output_file, outfile=diagram_output)
        print(f"Diagramme de paquetage UML généré : {diagram_output}")
    except Exception as e:
        print(f"Erreur lors de la génération de l'image : {e}")


# Exemple de paquetages et relations
packages = {
    "UserManagement": ["User", "District", "FarmerGroup"],
    "FarmManagement": ["Farm", "FarmData", "Point"],
    "CropManagement": ["Crop", "ProduceCategory", "Grade", "CropCoefficient", "Irrigation"],
    "EnvironmentalData": ["Weather", "SoilData", "Solar"],
}

# Définir les relations entre les classes et paquetages
relations = [
    "User --> District : manages",
    "User --> FarmerGroup : belongs to",
    "Farm --> FarmerGroup : managed by",
    "Crop --> ProduceCategory : categorized as",
    "Weather --> SoilData : affects",
]

# Générer le diagramme
generate_package_diagram(packages, relations)
