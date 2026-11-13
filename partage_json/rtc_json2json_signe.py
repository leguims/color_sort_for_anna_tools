import glob
import os
import json
import hmac
import hashlib

# Clé secrète au format texte
CLE_SIGNATURE = "b[zr8Jel$PDq'y;!lh%X_:eu1T%FQQ6,&><mNKau"

def signer_donnees(dictionnaire_entree):
    """Génère l'enveloppe signée HMAC-SHA256 à partir d'un dictionnaire brut."""
    donnees_json_str = json.dumps(dictionnaire_entree, ensure_ascii=False, separators=(',', ':'))

    # Transcription de la clé texte en buffer pour hmac.new
    signature = hmac.new(
        CLE_SIGNATURE.encode('utf-8'),
        donnees_json_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    enveloppe_finale = {
        "algorithme": "HMAC-SHA256",
        "donnees_json": donnees_json_str,
        "signature": signature,
        "version": 1
    }

    return enveloppe_finale

def traiter_fichiers_bruts():
    # Recherche de tous les fichiers JSON du répertoire
    tous_les_json = glob.glob("*.json")
    
    # Filtrage pour ne garder que les fichiers inconnus/bruts selon vos règles
    fichiers_bruts = [
        f for f in tous_les_json 
        if not f.startswith("rtc_") 
        and not f.startswith("non-signe_") 
        and not f.lower().startswith("synthese")
    ]

    if not fichiers_bruts:
        print("❌ Aucun fichier JSON brut à signer trouvé dans le répertoire.")
        return

    for chemin_fichier in fichiers_bruts:
        print(f"📖 Lecture et signature du fichier brut : {chemin_fichier}")
        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                donnees_brutes = json.load(f)
            
            # Génération de l'enveloppe signée
            enveloppe_signee = signer_donnees(donnees_brutes)
            
            # Extraction des métadonnées pour nommer proprement le fichier de sortie au format rtc_
            campagne_info = donnees_brutes.get("campagne", {})
            nom_campagne = campagne_info.get("campagne", "inconnue")
            nom_joueur = donnees_brutes.get("joueur", "inconnu")
            
            nom_fichier_sortie = f"rtc_{nom_campagne}_{nom_joueur}.json"
            
            # Enregistrement du fichier signé
            with open(nom_fichier_sortie, "w", encoding="utf-8") as f_out:
                json.dump(enveloppe_signee, f_out, ensure_ascii=False, indent=4)
                
            print(f"💾 Fichier signé généré avec succès : {nom_fichier_sortie}")
            
        except Exception as e:
            print(f"⚠️ Erreur lors du traitement de {chemin_fichier} : {e}")

if __name__ == "__main__":
    traiter_fichiers_bruts()