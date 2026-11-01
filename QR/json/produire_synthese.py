import glob
import os
import json

MODELE_SYNTHESE = "Synthese.json"

def lancer_synthese():
    # 1. Vérification de la présence du modèle de synthèse
    if not os.path.exists(MODELE_SYNTHESE):
        print(f"❌ Erreur : Le fichier modèle '{MODELE_SYNTHESE}' est introuvable dans le répertoire courant.")
        return

    # Recherche de tous les fichiers JSON du répertoire (sauf les fichiers de synthèse)
    fichiers_json = glob.glob("*.json")
    fichiers_joueurs = [f for f in fichiers_json if not f.startswith("Synthese")]
    
    print(f"📖 Chargement du modèle : {MODELE_SYNTHESE}")
    with open(MODELE_SYNTHESE, "r", encoding="utf-8") as f:
        synthese_data = json.load(f)
        
    # Extraction du nom de la campagne pour nommer le fichier de sortie
    nom_campagne = synthese_data.get("campagne", {}).get("campagne", "inconnue")
    
    # Nettoyage sécurisé du nom de campagne pour le fichier de sortie
    nom_campagne_propre = "".join(c for c in nom_campagne if c.isalnum() or c in ('_', '-', '[', ']'))
    fichier_sortie = f"Synthese_{nom_campagne_propre}.json"

    # Dictionnaire temporaire pour stocker toutes les durées par plateau (identifié par son "nom")
    # Structure : { nom_plateau: [durée_joueur_1, durée_joueur_2, ...] }
    suivi_plateaux_durees = {}

    # 2. Parcours de chaque fichier de joueur
    for chemin_joueur in fichiers_joueurs:
        print(f"👤 Traitement du fichier joueur : {chemin_joueur}")
        try:
            with open(chemin_joueur, "r", encoding="utf-8") as f:
                donnees_joueur = json.load(f)
        except Exception as e:
            print(f"⚠️ Impossible de lire {chemin_joueur} : {e}")
            continue
            
        nom_joueur = donnees_joueur.get("joueur")
        campagne_joueur = donnees_joueur.get("campagne", {})
        niveaux_joueur = campagne_joueur.get("niveaux", [])
        
        if not nom_joueur:
            print(f"⚠️ Nom de joueur introuvable dans {chemin_joueur}, ignoré.")
            continue
            
        synthese_niveaux = synthese_data.get("campagne", {}).get("niveaux", [])
        
        # 3. Association des résultats des plateaux dans la structure de synthèse
        for niv_joueur in niveaux_joueur:
            plateaux_joueur = niv_joueur.get("plateaux", [])
            
            for plat_joueur in plateaux_joueur:
                nom_plateau = plat_joueur.get("nom")
                statut = plat_joueur.get("statut", "").strip().lower()
                duree = float(plat_joueur.get("duree", plat_joueur.get("durée", 0.0)))
                
                # Vérification du statut réussi
                if statut in ["réussi", "reussi"] and nom_plateau:
                    plateau_trouve = False
                    for niv_synth in synthese_niveaux:
                        for plat_synth in niv_synth.get("plateaux", []):
                            if plat_synth.get("nom") == nom_plateau:
                                # Cumul de la durée pour ce joueur sur ce plateau
                                ancienne_duree = plat_synth.get(nom_joueur, 0.0)
                                nouvelle_duree = ancienne_duree + duree
                                plat_synth[nom_joueur] = nouvelle_duree
                                
                                # Enregistrement pour le calcul global des statistiques du plateau
                                if nom_plateau not in suivi_plateaux_durees:
                                    suivi_plateaux_durees[nom_plateau] = []
                                suivi_plateaux_durees[nom_plateau].append(nouvelle_duree)
                                
                                plateau_trouve = True
                                break
                        if plateau_trouve:
                            break

    # 4. Ajout de la clé "duree" (min, mediane, moyenne, max) pour chaque plateau traité
    synthese_niveaux = synthese_data.get("campagne", {}).get("niveaux", [])
    for niv_synth in synthese_niveaux:
        for plat_synth in niv_synth.get("plateaux", []):
            nom_plateau = plat_synth.get("nom")
            if nom_plateau in suivi_plateaux_durees:
                liste_durees = suivi_plateaux_durees[nom_plateau]
                if liste_durees:
                    # Calcul de la médiane
                    liste_triee = sorted(liste_durees)
                    n = len(liste_triee)
                    if n % 2 == 1:
                        mediane_val = liste_triee[n // 2]
                    else:
                        mediane_val = (liste_triee[(n // 2) - 1] + liste_triee[n // 2]) / 2.0

                    plat_synth["duree"] = {
                        "min": round(min(liste_durees), 2),
                        "mediane": round(mediane_val, 2),
                        "moyenne": round(sum(liste_durees) / len(liste_durees), 2),
                        "max": round(max(liste_durees), 2)
                    }

    # 5. Enregistrement du fichier de synthèse final
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(synthese_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n✨ Synthèse générée et mise à jour avec succès dans : {fichier_sortie}")

if __name__ == "__main__":
    lancer_synthese()