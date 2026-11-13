import os
import sys

# Ajout du répertoire courant au PYTHONPATH pour permettre l'import des modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import des scripts du pipeline
import rtc_json_signe2synthese
import rtc_infographie_synthese

# Liste des répertoires à cibler
REPERTOIRES = ["1ESSAI", "2ESSAIS", "3ESSAIS", "TOUT"]

def executer_pipeline():
    repertoire_initial = os.getcwd()

    for dossier in REPERTOIRES:
        print(f"\n==========================================")
        print(f"📂 Traitement du répertoire : {dossier}")
        print(f"==========================================")

        if not os.path.isdir(dossier):
            print(f"⚠️ Le répertoire '{dossier}' n'existe pas. Passage au suivant.")
            continue

        try:
            # Se positionner dans le répertoire cible
            os.chdir(dossier)
            print(f"📍 Positionné dans : {os.getcwd()}")

            # 1. Exécution de la synthèse
            print("⏳ Exécution de la synthèse...")
            rtc_json_signe2synthese.lancer_synthese()

            # 2. Exécution de l'infographie
            print("⏳ Génération de l'infographie...")
            rtc_infographie_synthese.generer_infographie()

        except Exception as e:
            print(f"❌ Erreur lors du traitement du répertoire '{dossier}' : {e}")

        finally:
            # Retour au répertoire d'origine pour le tour suivant
            os.chdir(repertoire_initial)

    print("\n✨ Traitement de tous les répertoires terminé.")

if __name__ == "__main__":
    executer_pipeline()