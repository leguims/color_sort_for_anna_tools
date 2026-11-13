import glob
import os
import json
import hmac
import hashlib

MODELE_SYNTHESE = "../Synthese.json"
# DEBUG # MODELE_SYNTHESE = "partage_json/Synthese.json"
# Clé secrète au format texte
CLE_SIGNATURE = "b[zr8Jel$PDq'y;!lh%X_:eu1T%FQQ6,&><mNKau"

def verifier_signature(donnees_json_str, signature_attendue):
    """Vérifie l'intégrité des données en convertissant la clé texte en buffer."""
    signature_calculee = hmac.new(
        CLE_SIGNATURE.encode('utf-8'),
        donnees_json_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature_calculee, signature_attendue)

def lancer_synthese():
    if not os.path.exists(MODELE_SYNTHESE):
        print(f"❌ Erreur : Le fichier modèle '{MODELE_SYNTHESE}' est introuvable dans le répertoire courant.")
        return

    fichiers_joueurs = glob.glob("rtc_*.json")
    # DEBUG # fichiers_joueurs = glob.glob("partage_json/1ESSAI/rtc_*.json")
    
    if not fichiers_joueurs:
        print("❌ Aucun fichier joueur 'rtc_*.json' trouvé dans le répertoire.")
        return

    print(f"📖 Chargement du modèle : {MODELE_SYNTHESE}")
    with open(MODELE_SYNTHESE, "r", encoding="utf-8") as f:
        synthese_data = json.load(f)
        
    nom_campagne = synthese_data.get("campagne", {}).get("campagne", "inconnue")
    nom_campagne_propre = "".join(c for c in nom_campagne if c.isalnum() or c in ('_', '-', '[', ']'))
    fichier_sortie = f"Synthese_{nom_campagne_propre}.json"

    suivi_plateaux_durees = {}

    for chemin_joueur in fichiers_joueurs:
        if chemin_joueur.startswith("Synthese") or chemin_joueur.startswith("non-signe_"):
            continue

        print(f"👤 Traitement du fichier joueur : {chemin_joueur}")
        try:
            with open(chemin_joueur, "r", encoding="utf-8") as f:
                enveloppe_joueur = json.load(f)
            
            donnees_brutes_str = enveloppe_joueur.get("donnees_json", "")
            signature_fournie = enveloppe_joueur.get("signature", "")
            
            if not verifier_signature(donnees_brutes_str, signature_fournie):
                print(f"🚨 ERREUR DE SÉCURITÉ : Signature invalide pour {chemin_joueur}. Fichier ignoré.")
                continue
            
            donnees_joueur = json.loads(donnees_brutes_str)
                
        except Exception as e:
            print(f"⚠️ Impossible de lire ou valider {chemin_joueur} : {e}")
            continue
            
        nom_joueur = donnees_joueur.get("joueur")
        campagne = donnees_joueur.get("campagne", {})
        niveaux = campagne.get("niveaux", [])
        
        if not nom_joueur:
            print(f"⚠️ Nom de joueur introuvable dans {chemin_joueur}, ignoré.")
            continue
            
        synthese_niveaux = synthese_data.get("campagne", {}).get("niveaux", [])
        
        for niveau in niveaux:
            plateaux = niveau.get("plateaux", [])
            
            for plateau in plateaux:
                nom_plateau = plateau.get("nom")
                gameplay_plateau = plateau.get("gameplay")
                statut = plateau.get("statut", "").strip().lower()
                duree = float(plateau.get("duree", 0.0))
                
                if statut in ["reussi", "passé", "abandonné"] and nom_plateau:
                    plateau_trouve = False
                    # L'enregistrer dans la synthese
                    for niveau_synthese in synthese_niveaux:
                        for plateau_synthese in niveau_synthese.get("plateaux", []):
                            if plateau_synthese.get("nom") == nom_plateau \
                                and plateau_synthese.get("gameplay") == gameplay_plateau:
                                ancienne_duree = plateau_synthese.get(nom_joueur, 0.0)
                                nouvelle_duree = ancienne_duree + duree
                                plateau_synthese[nom_joueur] = nouvelle_duree
                                
                                # Derniere iteration du plateau
                                if statut in ["reussi", "passé"]:
                                    if gameplay_plateau not in suivi_plateaux_durees:
                                        suivi_plateaux_durees[gameplay_plateau] = {}
                                    if nom_plateau not in suivi_plateaux_durees[gameplay_plateau]:
                                        suivi_plateaux_durees[gameplay_plateau][nom_plateau] = []
                                    suivi_plateaux_durees[gameplay_plateau][nom_plateau].append(nouvelle_duree)
                                
                                plateau_trouve = True
                                break
                        if plateau_trouve:
                            break

    synthese_niveaux = synthese_data.get("campagne", {}).get("niveaux", [])
    for niveau_synthese in synthese_niveaux:
        for plateau_synthese in niveau_synthese.get("plateaux", []):
            nom_plateau = plateau_synthese.get("nom")
            gameplay_plateau = plateau_synthese.get("gameplay")
            if gameplay_plateau in suivi_plateaux_durees \
                and nom_plateau in suivi_plateaux_durees[gameplay_plateau]:
                liste_durees = suivi_plateaux_durees[gameplay_plateau][nom_plateau]
                if liste_durees:
                    liste_triee = sorted(liste_durees)
                    n = len(liste_triee)
                    if n % 2 == 1:
                        mediane_val = liste_triee[n // 2]
                    else:
                        mediane_val = (liste_triee[(n // 2) - 1] + liste_triee[n // 2]) / 2.0

                    plateau_synthese["duree"] = {
                        "min": round(min(liste_durees), 2),
                        "mediane": round(mediane_val, 2),
                        "moyenne": round(sum(liste_durees) / len(liste_durees), 2),
                        "max": round(max(liste_durees), 2)
                    }

    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(synthese_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n✨ Synthèse générée et mise à jour avec succès dans : {fichier_sortie}")

if __name__ == "__main__":
    lancer_synthese()