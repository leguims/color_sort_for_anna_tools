"Parcourt les plateaux resolus et les rassemble dans le fichier 'Solutions_classees.json' par difficulte avec une ecriture universelle"
import datetime
import time
import copy
import logging
import pathlib

import color_wood_sort as cws

COLONNES = range(3, 8) # [2] # range(2, 12)
LIGNES = range(3, 8) # [2] # range(2, 5)
PERIODE_SCRUTATION_SECONDES = 30*60
# Filtrer les plateaux a 2 lignes ou 2 colonnes qui sont trop triviaux et repetitifs.
COLONNES_VIDES_MAX = 1
PROFILER_LE_CODE = False
NOM_TACHE = 'classer_les_solutions'
FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'
NOMBRE_DE_COUPS_MINIMUM = 3


def classer_les_solutions(colonnes, lignes, nb_coups_min = NOMBRE_DE_COUPS_MINIMUM, taciturne=False):
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"{colonnes}.{lignes}.{NOM_TACHE}")
    if not taciturne:
        logger.info(f"DEBUT")
    # logger.info(plateau.plateau_ligne_texte_universel)
    lot_de_plateaux = cws.LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX))
    if lot_de_plateaux.est_deja_termine(): # or True: # True = Classe toutes les solutions a l'heure actuel.
        if not taciturne:
            logger.info("Ce lot de plateaux est termine")

        solutions_classees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export='Solutions_classees', repertoire='Solutions')
        solutions_classees = solutions_classees_json.importer()
        plateau = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)

        liste_plateaux_avec_solutions = lot_de_plateaux.to_dict().get('liste difficulte des plateaux')
        if "liste difficulte des plateaux" not in solutions_classees:
            solutions_classees["liste difficulte des plateaux"] = {}
        dict_difficulte = solutions_classees["liste difficulte des plateaux"]
        # Filtrer les plateaux sans solutions ou trop triviaux
        for difficulte, dico_nb_coups in liste_plateaux_avec_solutions.items():
            for nb_coups, liste_plateaux in dico_nb_coups.items():
                logger.info(f"\n\r - Difficulte : {difficulte} en {nb_coups} coups : {len(liste_plateaux)} plateau{pluriel(liste_plateaux, 'x')}")
                if difficulte is not None and nb_coups is not None and int(nb_coups) >= nb_coups_min :
                    if difficulte not in dict_difficulte:
                        dict_difficulte[str(difficulte)] = {}
                    if nb_coups not in dict_difficulte[str(difficulte)]:
                        dict_difficulte[str(difficulte)][str(nb_coups)] = []
                    for plateau_ligne_texte_universel in liste_plateaux:
                        plateau.clear()
                        plateau.plateau_ligne_texte_universel = plateau_ligne_texte_universel
                        dict_difficulte[str(difficulte)][str(nb_coups)].append(plateau.plateau_ligne_texte_universel)
        ordonner_difficulte_nombre_coups(solutions_classees["liste difficulte des plateaux"])
        solutions_classees_json.forcer_export(solutions_classees)
    else:
        if not taciturne:
            logger.info(" - Ce lot de plateaux n'est pas encore termine, pas de classement de solutions.")

# Copie de 'LotDePlateaux.arret_des_enregistrements_de_difficultes_plateaux()'
def ordonner_difficulte_nombre_coups(ensemble_des_difficultes_de_plateaux):
    "Methode qui classe les difficultes et nombres de coups des solutions"
    # Classement des difficultes
    cles_difficulte = list(ensemble_des_difficultes_de_plateaux.keys())
    if None in cles_difficulte:
        cles_difficulte.remove(None) # None est inclassable avec 'list().sort()'
    cles_difficulte.sort()
    dico_difficulte_classe = {k: ensemble_des_difficultes_de_plateaux[k] for k in cles_difficulte}
    if None in ensemble_des_difficultes_de_plateaux:
        dico_difficulte_classe[None] = ensemble_des_difficultes_de_plateaux[None]
    ensemble_des_difficultes_de_plateaux.clear()
    ensemble_des_difficultes_de_plateaux.update(dico_difficulte_classe)
    
    # Classement du nombre de coups
    for difficulte, dico_nb_coups in ensemble_des_difficultes_de_plateaux.items():
        cles_nb_coups = list(dico_nb_coups.keys())
        if None in cles_nb_coups:
            cles_nb_coups.remove(None) # None est inclassable avec 'list().sort()'
        cles_nb_coups.sort()
        dico_nb_coups_classe = {k: dico_nb_coups[k] for k in cles_nb_coups}
        if None in dico_nb_coups:
            dico_nb_coups_classe[None] = dico_nb_coups[None]
        dico_nb_coups.clear()
        dico_nb_coups.update(dico_nb_coups_classe)

def afficher_synthese():
    logger = logging.getLogger(f"chercher.afficher_synthese")
    logger.info(f"*** Synthese des Solutions:")
    solutions_classees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export='Solutions_classees', repertoire='Solutions')
    solutions_classees = solutions_classees_json.importer()

    somme_plateaux = 0
    for difficulte, dico_nb_coups in solutions_classees.get('liste difficulte des plateaux').items():
        for nb_coups, liste_plateaux in dico_nb_coups.items():
            logger.info(f" - Difficulte : {difficulte} en {nb_coups} coups : {len(liste_plateaux)} plateau{pluriel(liste_plateaux, 'x')}")
            if difficulte != 'None':
                somme_plateaux += len(liste_plateaux)
    logger.info(f" - Total : {somme_plateaux} plateau{pluriel(range(somme_plateaux), 'x')} valide{pluriel(range(somme_plateaux), 's')}")

def pluriel(LIGNES, lettre='s'):
    return lettre if len(LIGNES) > 1 else ""

def chercher_en_boucle():
    logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")

    taciturne = False # 1ere iteration n'est pas taciturne
    while(True):
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for lignes in LIGNES:
            for colonnes in COLONNES:
                classer_les_solutions(colonnes, lignes, taciturne=taciturne)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        logger.info(f"{current_time} - Attente entre 2 iterations de {PERIODE_SCRUTATION_SECONDES}s...")
        time.sleep(PERIODE_SCRUTATION_SECONDES)
        taciturne = True

def chercher_en_sequence():
    profil = cws.ProfilerLeCode('chercher_des_solutions', PROFILER_LE_CODE)
    profil.start()

    # Effacer l'existant
    solutions_classees_json = cws.ExportJSON(0, 0, '', nom_export='Solutions_classees', repertoire='Solutions')
    solutions_classees_json.effacer()
    
    logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
    for lignes in LIGNES:
        for colonnes in COLONNES:
            classer_les_solutions(colonnes, lignes)
    profil.stop()

    afficher_synthese()

if __name__ == "__main__":
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # chercher_en_boucle()
    chercher_en_sequence()
