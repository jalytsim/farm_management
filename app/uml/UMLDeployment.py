from plantuml import PlantUML

def generate_deployment_diagram(components):
    """
    Génère un diagramme de déploiement UML.

    Args:
        components (list): Liste des composants et des relations sous forme de tuples (source, destination, relation).
    """
    uml_code = ["@startuml"]

    # Définition des noeuds
    uml_code.append("node Serveur_Web {")
    uml_code.append("  [Application React]")  # Application React hébergée
    uml_code.append("}")

    uml_code.append("node Serveur_Backend {")
    uml_code.append("  [API Flask Backend]")  # API Flask hébergée
    uml_code.append("}")

    uml_code.append("database Serveur_BDD {")
    uml_code.append("  [Base de Données MySQL]")  # Base de données
    uml_code.append("}")

    uml_code.append("node API_Externe {")
    uml_code.append("  [Service Externe]")  # APIs externes
    uml_code.append("}")

    # Ajout des relations
    for component in components:
        source, destination, relation = component
        uml_code.append(f"{source} --> {destination}: {relation}")

    uml_code.append("@enduml")

    # Sauvegarde et génération
    uml_content = "\n".join(uml_code)
    output_file = "deployment_diagram.puml"
    with open(output_file, "w") as file:
        file.write(uml_content)

    # Génération du diagramme
    plantuml_server = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    diagram_output = output_file.replace(".puml", ".png")
    try:
        plantuml_server.processes_file(output_file, outfile=diagram_output)
        print(f"Diagramme de déploiement UML généré : {diagram_output}")
    except Exception as e:
        print(f"Erreur lors de la génération de l'image : {str(e)}")

# Exemple d'utilisation
components = [
    ("[Application React]", "[API Flask Backend]", "Requêtes API"),
    ("[API Flask Backend]", "[Base de Données MySQL]", "Requêtes SQL"),
    ("[API Flask Backend]", "[Service Externe]", "Requêtes vers API"),
    ("Utilisateur", "[Application React]", "Navigateur Web")
]

generate_deployment_diagram(components)
