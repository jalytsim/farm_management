import os
import subprocess


def fichiers_non_ignores(repo):
    """
    Récupère les fichiers non ignorés par git
    """
    result = subprocess.run(
        ["git", "ls-files", "--others", "--cached", "--exclude-standard"],
        cwd=repo,
        stdout=subprocess.PIPE,
        text=True
    )

    return result.stdout.splitlines()


def construire_arbre(fichiers):
    arbre = {}

    for fichier in fichiers:
        parties = fichier.split("/")
        node = arbre

        for p in parties:
            node = node.setdefault(p, {})

    return arbre


def afficher_arbre(node, prefix=""):
    elements = sorted(node.keys())

    lignes = []

    for i, e in enumerate(elements):
        dernier = i == len(elements) - 1

        branche = "└── " if dernier else "├── "
        nouveau_prefix = prefix + ("    " if dernier else "│   ")

        lignes.append(prefix + branche + e)

        lignes.extend(afficher_arbre(node[e], nouveau_prefix))

    return lignes


if __name__ == "__main__":

    dossier = input("Chemin du repo : ").strip()

    fichiers = fichiers_non_ignores(dossier)

    arbre = construire_arbre(fichiers)

    resultat = [dossier]
    resultat.extend(afficher_arbre(arbre))

    with open("arborescence.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(resultat))

    print("✅ Arborescence générée")