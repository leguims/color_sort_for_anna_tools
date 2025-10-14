"Parcourt les plateaux exhaustifs et en trouve les solutions 'ColorWoodSort'"
import datetime
import time
import logging
import pathlib

from plateau import Plateau
from lot_de_plateaux import LotDePlateaux
from resoudre_plateau import ResoudrePlateau
from profiler_le_code import ProfilerLeCode

PERIODE_SCRUTATION_SECONDES = 30*60
COLONNES = [3] # range(2, 12) #[7] # range(2, 6) # [2] # range(2, 12)
LIGNES =  [3] # range(2,7) #range(2, 14) #range(2, 3) # [2] # range(2, 5)
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 500_000
PROFILER_LE_CODE = False
NOM_TACHE = 'chercher_des_solutions'
FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'
PERIODE_AFFICHAGE = 5*60 # en secondes
REPERTOIRE_ANALYSE = 'Analyse_nouvelle_architecture'
REPERTOIRE_SOLUTION = 'Solutions_nouvelle_architecture'

def chercher_des_solutions(colonnes, lignes, taciturne=False):
    # Configurer le logger
    logger = logging.getLogger(f"{colonnes}.{lignes}.{NOM_TACHE}")
    if not taciturne:
        logger.info(f"DEBUT")

    plateau = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
    lot_de_plateaux = LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX),
                                    repertoire_export_json=REPERTOIRE_ANALYSE,
                                    nb_plateaux_max = MEMOIRE_MAX)
    if lot_de_plateaux.est_deja_termine(): # or True: # True = Chercher toutes les solutions a l'heure actuel.
        if not taciturne:
            logger.info("Ce lot de plateaux est termine")

        if lot_de_plateaux.nb_plateaux_valides != lot_de_plateaux.nb_plateaux_solutionnes:
            if lot_de_plateaux.nb_plateaux_valides < lot_de_plateaux.nb_plateaux_solutionnes:
                logger.info(f"Il y a plus de plateaux de solutions que de plateaux valides ! Il y a un probleme ! {lot_de_plateaux.nb_plateaux_solutionnes} > {lot_de_plateaux.nb_plateaux_valides}")
                # TODO : Il y a probablement des solutions de plateau obsoletes a effacer.
            logger.info(f"Il reste des solutions a trouver : {lot_de_plateaux.nb_plateaux_valides} != {lot_de_plateaux.nb_plateaux_solutionnes}")
            
            dernier_affichage  = datetime.datetime.now().timestamp() - PERIODE_AFFICHAGE
            nb_solutions_a_trouver = lot_de_plateaux.nb_plateaux_valides
            for plateau_ligne_texte_a_resoudre in lot_de_plateaux.plateaux_valides:
                plateau.clear()
                plateau.plateau_ligne_texte = plateau_ligne_texte_a_resoudre
                if not lot_de_plateaux.est_deja_connu_difficulte_plateau(plateau):
                    resolution = ResoudrePlateau(plateau,
                                                 repertoire_analyse=REPERTOIRE_ANALYSE,
                                                 repertoire_solution=REPERTOIRE_SOLUTION)
                    resolution.backtracking()
                    lot_de_plateaux.definir_difficulte_plateau(plateau, resolution.difficulte, resolution.solution_la_plus_courte)
                
                # Afficher si dernier affichage > 5mins
                nb_solutions_a_trouver -= 1
                if datetime.datetime.now().timestamp() - dernier_affichage > PERIODE_AFFICHAGE:
                    logger.info(f"Il reste {nb_solutions_a_trouver} solutions a resoudre.")
                    dernier_affichage  = datetime.datetime.now().timestamp()

            lot_de_plateaux.arret_des_enregistrements_de_difficultes_plateaux()
            for difficulte, dico_nb_coups in lot_de_plateaux.difficulte_plateaux.items():
                for nb_coups, liste_plateaux in dico_nb_coups.items():
                    logger.info(f"Difficulte : {difficulte} en {nb_coups} coups : {len(liste_plateaux)} plateau{pluriel(liste_plateaux, lettre='x')}")
        else:
            if not taciturne:
                logger.info("Toutes les solutions sont trouvees.")
    else:
        if not taciturne:
            logger.info("Ce lot de plateaux n'est pas encore termine, pas de recherche de solution.")

def pluriel(LIGNES, lettre='s'):
    return lettre if len(LIGNES) > 1 else ""

def chercher_en_boucle(colonnes=COLONNES, lignes=LIGNES):
    logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")

    logger.info('-'*10 + " 1ere RECHERCHE " + '-'*10)
    chercher_en_sequence() # 1ere iteration est bavarde
    while(True):
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for iter_lignes in lignes:
            for iter_colonnes in colonnes:
                chercher_des_solutions(iter_colonnes, iter_lignes, taciturne=True)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        logger.info(f"{current_time} - Attente entre 2 iterations de {PERIODE_SCRUTATION_SECONDES}s...")
        time.sleep(PERIODE_SCRUTATION_SECONDES)

def chercher_en_sequence(colonnes=COLONNES, lignes=LIGNES):
    profil = ProfilerLeCode('chercher_des_solutions', PROFILER_LE_CODE)
    profil.start()

    logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
    for iter_lignes in lignes:
        for iter_colonnes in colonnes:
            chercher_des_solutions(iter_colonnes, iter_lignes)
    profil.stop()

if __name__ == "__main__":
    # Configurer le logger
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # chercher_en_boucle()
    chercher_en_sequence()
