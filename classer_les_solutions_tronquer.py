"""Decoupe l'ensemble des solutions inter-plateaux en des ensembles plus petits de solutions
Adapte pour avoir un fichier de solutions restreint pour le jeu"""
import datetime
import time
import logging
import pathlib

import color_wood_sort as cws

PERIODE_SCRUTATION_SECONDES = 30*60
# Filtrer les plateaux a 2 lignes ou 2 colonnes qui sont trop triviaux et repetitifs.
PROFILER_LE_CODE = False
NOM_TACHE = 'tronquer_les_solutions'
FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

TAILLE = 10

def tronquer_les_solutions(taille = TAILLE, decallage = 0):
    # Configurer le logger
    logger = logging.getLogger(f"tronquer.{NOM_TACHE}")
    logger.info(f"\n\r*** Tronquer le classement des Solutions :")

    solutions_classees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export='Solutions_classees', repertoire='Solutions')
    solutions_classees = solutions_classees_json.importer()
    solutions_classees_tronquees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=f'Solutions_classees_T{taille}_D{decallage}', repertoire='Solutions')

    if "liste difficulte des plateaux" in solutions_classees:
        dict_difficulte = solutions_classees["liste difficulte des plateaux"]
        dict_difficulte_tronque = {}
        # Gommer la notion de 'nb_coups' pour le jeu
        for difficulte, dico_nb_coups in dict_difficulte.items():
            for nb_coups, liste_plateaux in dico_nb_coups.items():
                if difficulte not in dict_difficulte_tronque:
                    dict_difficulte_tronque[difficulte] = []
                dict_difficulte_tronque[difficulte] += liste_plateaux[decallage:decallage+taille]
        # Tronquer les solutions
        for difficulte, liste_plateaux in dict_difficulte_tronque.items():
            liste_plateaux = liste_plateaux[0:taille]
        solutions_classees["liste difficulte des plateaux"] = dict_difficulte_tronque
        solutions_classees_tronquees_json.forcer_export(solutions_classees)

def afficher_synthese(taille = TAILLE, decallage = 0):
    # Configurer le logger
    logger = logging.getLogger("tronquer.afficher_synthese")
    logger.info(f"*** Synthese des Solutions:")
    solutions_classees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=f'Solutions_classees_T{taille}_D{decallage}', repertoire='Solutions')
    solutions_classees = solutions_classees_json.importer()

    somme_plateaux = 0
    for difficulte, liste_plateaux in solutions_classees.get('liste difficulte des plateaux').items():
        logger.info(f" - Difficulte : {difficulte} - {len(liste_plateaux)} plateau{pluriel(liste_plateaux, 'x')}")
        if difficulte != 'None':
            somme_plateaux += len(liste_plateaux)
    logger.info(f" - Total : {somme_plateaux} plateau{pluriel(range(somme_plateaux), 'x')} valide{pluriel(range(somme_plateaux), 's')}")

def pluriel(LIGNES, lettre='s'):
    return lettre if len(LIGNES) > 1 else ""

def chercher_en_boucle():
    # Configurer le logger
    logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")
    while(True):
        tronquer_les_solutions()
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        logger.info(f"{current_time} - Attente entre 2 iterations de {PERIODE_SCRUTATION_SECONDES}s...")
        time.sleep(PERIODE_SCRUTATION_SECONDES)

def chercher_en_sequence():
    profil = cws.ProfilerLeCode('chercher_des_solutions', PROFILER_LE_CODE)
    profil.start()

    # Configurer le logger
    logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
    for i in range(10):
        # Effacer l'existant
        #solutions_classees_json = cws.ExportJSON(0, 0, '', nom_export=f'Solutions_classees_T{TAILLE}_D{i * TAILLE}', repertoire='Solutions')
        solutions_classees_json = cws.ExportJSON(0, 0, '', nom_export=f'Solutions_classees_T{(i+1)*TAILLE}_D{0}', repertoire='Solutions')
        solutions_classees_json.effacer()
        
        # tronquer_les_solutions(TAILLE, i * TAILLE)
        tronquer_les_solutions((i+1) * TAILLE, 0)
        profil.stop()

        afficher_synthese()

if __name__ == "__main__":
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # chercher_en_boucle()
    chercher_en_sequence()
