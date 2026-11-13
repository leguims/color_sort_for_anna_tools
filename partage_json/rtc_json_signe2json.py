import glob
import os
import json
import hmac
import hashlib

# Clé secrète partagée (doit correspondre à celle utilisée lors de la signature)
CLE_SIGNATURE = "b[zr8Jel$PDq'y;!lh%X_:eu1T%FQQ6,&><mNKau"

def verifier_signature(donnees_json_str, signature_attendue):
    """Vérifie l'intégrité des données en recalculant le HMAC-SHA256."""
    signature_calculee = hmac.new(
        CLE_SIGNATURE.encode('utf-8'),
        donnees_json_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature_calculee, signature_attendue)

def convertir_json_signe():
    # Recherche de tous les fichiers de joueurs signés
    fichiers_signes = glob.glob("rtc_*.json")
    
    if not fichiers_signes:
        print("❌ Aucun fichier 'rtc_*.json' trouvé dans le répertoire.")
        return

    for chemin_fichier in fichiers_signes:
        # Évite de traiter d'éventuels fichiers de synthèse ou déjà convertis
        if chemin_fichier.startswith("Synthese") or chemin_fichier.startswith("non-signe_"):
            continue
            
        print(f"📖 Traitement du fichier : {chemin_fichier}")
        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                enveloppe = json.load(f)
            
            donnees_brutes_str = enveloppe.get("donnees_json", "")
            signature_fournie = enveloppe.get("signature", "")
            
            # 1. Vérification de la signature cryptographique
            if not verifier_signature(donnees_brutes_str, signature_fournie):
                print(f"🚨 ERREUR DE SÉCURITÉ : Signature invalide pour {chemin_fichier}. Fichier rejeté.")
                continue
            
            # 2. Désérialisation de la chaîne stringify en objet JSON natif
            donnees_natives = json.loads(donnees_brutes_str)
            
            # 3. Détermination du nom de fichier de sortie avec le préfixe "non-signe_"
            nom_base = os.path.basename(chemin_fichier)
            fichier_sortie = f"non-signe_{nom_base}"
            
            # 4. Enregistrement du JSON épuré (avec indentation pour la lisibilité)
            with open(fichier_sortie, "w", encoding="utf-8") as f_out:
                json.dump(donnees_natives, f_out, ensure_ascii=False, indent=4)
                
            print(f"✅ Succès : Données extraites et enregistrées dans {fichier_sortie}")
            
        except Exception as e:
            print(f"⚠️ Erreur lors du traitement de {chemin_fichier} : {e}")

if __name__ == "__main__":
    convertir_json_signe()