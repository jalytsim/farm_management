import random

# Liste des technologies Java
technologies_java = [
   
    "JMS (Java Message Service)",
 
    "JAX-RS (Java API for RESTful Web Services)",
  
    "JMX (Java Management Extensions)"
 
]

# Sélectionner aléatoirement une technologie
tech_random = random.choice(technologies_java)

# Afficher la technologie sélectionnée
print("Technologie Java sélectionnée aléatoirement : ", tech_random)
