import os
import shutil
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from tkinter.filedialog import askdirectory

def organize_files_by_extension(directory):
    """
    Organize files in the specified directory into folders named after their extensions.

    :param directory: Path to the directory containing the files to organize
    """
    if not os.path.exists(directory):
        Messagebox.show_error(f"Le répertoire {directory} n'existe pas.")
        return

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if os.path.isfile(filepath):
            extension = os.path.splitext(filename)[1][1:]  # Remove the dot (.)

            if extension:
                extension_folder = os.path.join(directory, extension)

                if not os.path.exists(extension_folder):
                    os.makedirs(extension_folder)

                shutil.move(filepath, os.path.join(extension_folder, filename))

    Messagebox.show_info("Organisation terminée !", "Les fichiers ont été organisés avec succès.")

def on_organize():
    directory = askdirectory(title="Sélectionnez un répertoire")
    if directory:
        organize_files_by_extension(directory)
    else:
        Messagebox.show_warning("Veuillez sélectionner un répertoire valide.")

# Create the main application window
app = ttk.Window(themename="superhero")
app.title("Organisateur de Fichiers")
app.geometry("400x200")

# Create a label
label = ttk.Label(app, text="Cliquez sur le bouton pour sélectionner un répertoire à organiser :", font=("Helvetica", 12))
label.pack(pady=10)

# Create an organize button
organize_button = ttk.Button(app, text="Parcourir et Organiser", command=on_organize, bootstyle="primary")
organize_button.pack(pady=10)

# Run the application
app.mainloop()
