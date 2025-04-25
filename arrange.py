import json
import pandas as pd
from tkinter import Tk, filedialog, messagebox
import os

def convert_json_to_excel():
    # Ouvre une boîte de dialogue pour choisir un fichier JSON
    file_path = filedialog.askopenfilename(
        title="Choisir un fichier JSON",
        filetypes=[("Fichiers JSON", "*.json")]
    )

    if not file_path:
        return  # Annule si aucun fichier n'est sélectionné

    try:
        # Charger le fichier JSON
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Normaliser les données JSON
        df = pd.json_normalize(data["data"])

        # Créer le nom de fichier Excel
        base_name = os.path.splitext(file_path)[0]
        output_file = base_name + ".xlsx"

        # Sauvegarder le fichier Excel
        df.to_excel(output_file, index=False)

        messagebox.showinfo("Succès", f"Fichier converti avec succès :\n{output_file}")

    except Exception as e:
        print(f"Une erreur est survenue :\n{e}")
        messagebox.showerror("Erreur", f"Une erreur est survenue :\n{e}")

# Lancer la fenêtre principale
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Ne pas afficher la fenêtre principale
    convert_json_to_excel()
