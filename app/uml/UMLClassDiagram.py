from plantuml import PlantUML, PlantUMLHTTPError



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
    output_file = "class_diagram_admin.puml"
    with open(output_file, "w") as file:
        file.write(uml_content)

    # Generer le fichier image avec PlantUML
    plantuml_server = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    diagram_output = output_file.replace(".puml", ".png")
    plantuml_server.processes_file(output_file, outfile=diagram_output)

    print(f"Diagramme de classes UML genere: {diagram_output}")

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
    },
    "relations": [
      
    ]
}

generate_class_diagram(class_models)


