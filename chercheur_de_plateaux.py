"Module pour creer des plateaux de 'ColorWoodSort'"
from itertools import permutations
import logging
import pathlib
import datetime

import color_wood_sort as cws

COLONNES = [3] # range(2, 5) # range(2, 5) #11
LIGNES = [3] # [2,3] #4
COLONNES_VIDES_MAX = 1
PROFILER_LE_CODE = False
NOM_TACHE = 'chercher_des_plateaux'
FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'
PERIODE_AFFICHAGE = 5*60 # en secondes

def chercher_des_plateaux(colonnes, lignes):
    # Configurer le logger
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"{colonnes}.{lignes}.{NOM_TACHE}")
    logger.info(f"DEBUT")
    plateau = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
    plateau.creer_plateau_initial()
    # logger.info(plateau.plateau_ligne_texte_universel)
    lot_de_plateaux = cws.LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX))
    dernier_affichage  = datetime.datetime.now().timestamp()
    if not lot_de_plateaux.est_deja_termine():
        # lot_de_plateaux.fixer_taille_memoire_max(5)
        for permutation_courante in permutations(plateau.pour_permutations):
            # Verifier que ce plateau est nouveau
            permutation_courante = ''.join(permutation_courante)
            if not lot_de_plateaux.est_ignore(permutation_courante):
                # Afficher si dernier affichage > 5mins
                if datetime.datetime.now().timestamp() - dernier_affichage > PERIODE_AFFICHAGE:
                    logger.info(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
                    dernier_affichage  = datetime.datetime.now().timestamp()

        lot_de_plateaux.arret_des_enregistrements()
        # lot_de_plateaux.exporter_fichier_json()

        logger.info(f"duree={lot_de_plateaux.formater_duree(lot_de_plateaux.duree)}")

        logger.info(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
        logger.info(f"nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
    else:
        logger.info(f"Ce lot de plateaux est deja termine")


def chercher_en_sequence():
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
    for lignes in LIGNES:
        for colonnes in COLONNES:
            chercher_des_plateaux(colonnes, lignes)
    logger.info('-'*10 + " FIN " + '-'*10)

def chercher_en_parallele():
    profil = cws.ProfilerLeCode(NOM_TACHE, PROFILER_LE_CODE)
    profil.start()

    taches = cws.CreerLesTaches(nom=NOM_TACHE, nb_colonnes=max(COLONNES)+1, nb_lignes=max(LIGNES)+1)

    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"chercher_en_parallele.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)

    # taches.exporter()
    taches.importer()
    taches.executer_taches(chercher_des_plateaux)
    logger.info('-'*10 + " FIN " + '-'*10)

    profil.stop()

if __name__ == "__main__":
    chercher_en_parallele()
    # chercher_en_sequence()