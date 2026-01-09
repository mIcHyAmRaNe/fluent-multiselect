import os


def generer_fichier_code(dossier_source, fichier_sortie="code_source.py"):
    """
    Parcourt le dossier source et compile le contenu de tous les fichiers .py
    dans un seul fichier texte avec des en-têtes clairs.
    """
    # On vérifie si le dossier existe pour éviter les erreurs
    if not os.path.exists(dossier_source):
        print(f"Erreur : Le dossier '{dossier_source}' est introuvable.")
        return

    with open(fichier_sortie, "w", encoding="utf-8") as out:
        for root, _, files in os.walk(dossier_source):
            for file in files:
                if (
                    file.endswith(".py") and file != "__init__.py"
                ):  # Optionnel: ignorer les init vides
                    chemin_complet = os.path.join(root, file)

                    # On écrit le chemin relatif pour la clarté
                    out.write(f"# FILE: {chemin_complet}\n")

                    try:
                        with open(chemin_complet, "r", encoding="utf-8") as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"# Erreur de lecture : {e}\n")

                    out.write("\n\n")


if __name__ == "__main__":
    # Chemin vers votre package
    target_dir = os.path.join("src", "fluent_multiselect")
    generer_fichier_code(target_dir)
    print(f"✅ Terminé ! Le code a été rassemblé dans 'code_source.py'")