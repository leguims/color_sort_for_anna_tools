import glob
import os
import json
import hmac
import hashlib
import re
from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol

# ==========================================
# CONFIGURATION
# ==========================================
CLE_SIGNATURE = "b[zr8Jel$PDq'y;!lh%X_:eu1T%FQQ6,&><mNKau"
LOG_ERREURS = "erreurs_signature.log"

def enregistrer_alerte(message, liste_erreurs):
    """Ajoute l'alerte à la liste en mémoire et l'écrit dans le fichier de log si besoin."""
    print(message)
    liste_erreurs.append(message)

def nettoyer_nom_fichier(texte):
    """Nettoie un texte pour l'utiliser en toute sécurité dans un nom de fichier."""
    if not texte:
        return "inconnu"
    texte_propre = re.sub(r'[\\/*?:"<>|]', "", str(texte))
    return texte_propre.strip().replace(" ", "_")

def verifier_signature(donnees_brutes_str, signature_recue, cle):
    """Vérifie la signature HMAC-SHA256 uniquement sur la chaîne brute de 'donnees_json'."""
    if cle == "VOTRE_CLE_SECRETE_ICI":
        return True  # Désactivé tant que la vraie clé n'est pas configurée
    try:
        h_base = hmac.new(cle.encode('utf-8'), donnees_brutes_str.encode('utf-8'), hashlib.sha256).hexdigest()
        if hmac.compare_digest(h_base, signature_recue):
            return True
            
        obj = json.loads(donnees_brutes_str)
        donnees_norm = json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
        h_norm = hmac.new(cle.encode('utf-8'), donnees_norm.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(h_norm, signature_recue)
    except Exception:
        return False

# ==========================================
# SCRIPT PRINCIPAL
# ==========================================
print("🔍 Recherche des images (JPG, JPEG, PNG) dans le répertoire courant...")

extensions = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
fichiers_bruts = []
for ext in extensions:
    fichiers_bruts.extend(glob.glob(ext))

fichiers_images = list(set(fichiers_bruts))

if not fichiers_images:
    print("❌ Aucune image trouvée dans ce répertoire.")
else:
    print(f"📁 {len(fichiers_images)} images uniques trouvées. Scan et vérification en cours...")

    regroupement_campagnes = {}
    joueur_reference = None
    journal_erreurs = []

    for chemin_image in fichiers_images:
        nom_fichier = os.path.basename(chemin_image)
        try:
            img = Image.open(chemin_image)
            resultats_qr = decode(img, symbols=[ZBarSymbol.QRCODE])
            
            if not resultats_qr:
                enregistrer_alerte(f"⚠️ [{nom_fichier}] Aucun QR code détecté.", journal_erreurs)
                continue
                
            for qr in resultats_qr:
                contenu_texte = qr.data.decode('utf-8')
                
                try:
                    qr_objet = json.loads(contenu_texte)
                except json.JSONDecodeError:
                    enregistrer_alerte(f"❌ [{nom_fichier}] Le contenu global du QR code n'est pas un JSON valide.", journal_erreurs)
                    continue
                
                if "donnees_json" not in qr_objet or "signature" not in qr_objet:
                    enregistrer_alerte(f"❌ [{nom_fichier}] Structure invalide : les clés 'donnees_json' et/ou 'signature' sont absentes. (Contenu reçu : {qr_objet})", journal_erreurs)
                    continue
                
                donnees_brutes_str = qr_objet["donnees_json"]
                signature_recue = qr_objet["signature"]
                
                # Vérification de la signature appliquée uniquement sur 'donnees_json'
                if not verifier_signature(donnees_brutes_str, signature_recue, CLE_SIGNATURE):
                    enregistrer_alerte(f"❌ [{nom_fichier}] ALERTE : Signature HMAC-SHA256 invalide pour 'donnees_json' ! (Signature reçue : {signature_recue})", journal_erreurs)
                    continue
                
                try:
                    donnees_utiles = json.loads(donnees_brutes_str)
                except json.JSONDecodeError:
                    enregistrer_alerte(f"❌ [{nom_fichier}] Le contenu interne de 'donnees_json' n'est pas un JSON valide.", journal_erreurs)
                    continue

                # Gestion et vérification du joueur
                joueur_courant = donnees_utiles.get("joueur", "Inconnu")
                
                if joueur_reference is None:
                    joueur_reference = joueur_courant
                elif joueur_courant != joueur_reference:
                    enregistrer_alerte(f"❌ [{nom_fichier}] ALERTE : Le joueur a changé ! Attendu : '{joueur_reference}', Trouvé : '{joueur_courant}'.", journal_erreurs)
                    continue

                # Normalisation des formats (Riche vs Plat)
                campagne_brute = donnees_utiles.get("campagne")
                
                if isinstance(campagne_brute, str):
                    nom_campagne = campagne_brute
                    campagne_info = {
                        "campagne": nom_campagne,
                        "date_debut": donnees_utiles.get("date_debut", 0.0),
                        "date_fin": donnees_utiles.get("date_fin", 0.0)
                    }
                    if "score" in donnees_utiles:
                        campagne_info["score"] = donnees_utiles.get("score")
                    
                    niveau_brut = donnees_utiles.get("niveau")
                    niveau_objet = {"niveau": niveau_brut, "plateaux": donnees_utiles.get("plateaux", [])} if isinstance(niveau_brut, str) else niveau_brut
                else:
                    campagne_info = campagne_brute if isinstance(campagne_brute, dict) else {}
                    nom_campagne = campagne_info.get("campagne", "campagne_inconnue")
                    niveau_objet = donnees_utiles.get("niveau")

                if isinstance(niveau_objet, dict):
                    nom_niveau = niveau_objet.get("niveau", "niveau_inconnu")
                elif isinstance(niveau_objet, str):
                    nom_niveau = niveau_objet
                    niveau_objet = {"niveau": nom_niveau}
                else:
                    nom_niveau = "niveau_inconnu"

                # Règles de concaténation
                if nom_campagne not in regroupement_campagnes:
                    campagne_info["niveaux"] = []
                    regroupement_campagnes[nom_campagne] = {
                        "joueur": joueur_reference,
                        "campagne": campagne_info
                    }
                else:
                    campagne_existante = regroupement_campagnes[nom_campagne]["campagne"]
                    date_fin_existante = campagne_existante.get("date_fin")
                    
                    niveaux_actuels = campagne_existante.get("niveaux", [])
                    campagne_info["niveaux"] = niveaux_actuels
                    
                    if date_fin_existante is None or date_fin_existante == 0.0:
                        regroupement_campagnes[nom_campagne]["campagne"] = campagne_info
                        regroupement_campagnes[nom_campagne]["campagne"]["niveaux"] = niveaux_actuels

                # Ajout du niveau dans la liste "niveaux" (sans doublon)
                niveaux_liste = regroupement_campagnes[nom_campagne]["campagne"]["niveaux"]
                if niveau_objet and not any(n.get("niveau") == nom_niveau for n in niveaux_liste):
                    niveaux_liste.append(niveau_objet)
                
        except Exception as e:
            enregistrer_alerte(f"❌ [{nom_fichier}] Erreur technique : {e}", journal_erreurs)

    # ==========================================
    # EXPORT DES RÉSULTATS
    # ==========================================
    if regroupement_campagnes:
        print(f"\n✅ Traitement terminé ! Génération du fichier JSON global...")

        for nom_campagne, contenu_groupe in regroupement_campagnes.items():
            j_propre = nettoyer_nom_fichier(contenu_groupe["joueur"])
            c_propre = nettoyer_nom_fichier(nom_campagne)
            
            nom_sortie_json = f"{j_propre}_{c_propre}.json"
            
            donnees_a_ecrire = {
                "joueur": contenu_groupe["joueur"],
                "campagne": contenu_groupe["campagne"]
            }
            
            with open(nom_sortie_json, "w", encoding="utf-8") as f_out:
                json.dump(donnees_a_ecrire, f_out, ensure_ascii=False, indent=4)

            print(f"📁 Fichier JSON unique généré : {nom_sortie_json}")
        
        # Gestion conditionnelle du fichier de log
        if len(journal_erreurs) > 0:
            with open(LOG_ERREURS, "w", encoding="utf-8") as f_log:
                f_log.write("--- RAPPORT D'ERREURS / INCIDENTS SIGNATURES & QR CODES ---\n\n")
                for err in journal_erreurs:
                    f_log.write(err + "\n")
            print(f"⚠️ {len(journal_erreurs)} alerte(s) ou erreur(s) consigné(s) dans : '{LOG_ERREURS}'")
        else:
            # S'il existe un vieux log d'une exécution précédente, on peut optionnellement le nettoyer
            if os.path.exists(LOG_ERREURS):
                os.remove(LOG_ERREURS)
            print("✨ Tout est parfait, aucune erreur détectée.")
    else:
        print(f"❌ Aucune donnée valide trouvée.")
        if len(journal_erreurs) > 0:
            with open(LOG_ERREURS, "w", encoding="utf-8") as f_log:
                f_log.write("--- RAPPORT D'ERREURS / INCIDENTS SIGNATURES & QR CODES ---\n\n")
                for err in journal_erreurs:
                    f_log.write(err + "\n")