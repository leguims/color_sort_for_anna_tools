"Module pour créer, résoudre et qualifier les solutions des plateaux de 'ColorWoodSort'"
from itertools import permutations #, product, combinations#, combinations_with_replacement
import logging
import pathlib

from plateau import Plateau
from lot_de_plateaux import LotDePlateaux
from resoudre_plateau import ResoudrePlateau
from profiler_le_code import ProfilerLeCode

COLONNES = [2] # range(2, 5) # range(2, 5) #11
LIGNES = [2] # [2,3] #4
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 500_000_000
PROFILER_LE_CODE = False
NOM_TACHE = 'chercher_les_plateaux_et_les_solutions'
FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

def chercher_les_plateaux_et_les_solutions(colonnes, lignes):
    # Configurer le logger
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"{colonnes}.{lignes}.{NOM_TACHE}")
    logger.info(f"DEBUT")
    plateau = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
    plateau.creer_plateau_initial()
    logger.info(plateau.plateau_ligne_texte_universel)
    lot_de_plateaux = LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX), nb_plateaux_max = MEMOIRE_MAX)
    if not lot_de_plateaux.est_deja_termine():
        # lot_de_plateaux.fixer_taille_memoire_max(5)
        for permutation_courante in permutations(plateau.pour_permutations):
            # Verifier que ce plateau est nouveau
            if not lot_de_plateaux.est_ignore(permutation_courante):
                if lot_de_plateaux.nb_plateaux_valides % 400 == 0:
                    logger.info(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")

        lot_de_plateaux.arret_des_enregistrements()
        # lot_de_plateaux.exporter_fichier_json()
        logger.info(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
        logger.info(f"nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
    else:
        logger.info("Ce lot de plateaux est déjà terminé")

    logger.info('*'*60 + ' RESOLUTION')
    for plateau_ligne_texte_a_resoudre in lot_de_plateaux.plateaux_valides:
        plateau.clear()
        plateau.plateau_ligne_texte = plateau_ligne_texte_a_resoudre
        resolution = ResoudrePlateau(plateau)
        resolution.backtracking()
        lot_de_plateaux.definir_difficulte_plateau(plateau, resolution.difficulte, resolution.solution_la_plus_courte)
        # logger.info(f"'{plateau_ligne_texte_a_resoudre}' : nombre de solutions = {resolution.nb_solutions}, solution moyenne = {resolution.solution_moyenne}, la plus courte = {resolution.solution_la_plus_courte}, la plus longue = {resolution.solution_la_plus_longue}")
        # logger.info(f"'{plateau_ligne_texte_a_resoudre}' : nombre de solutions = {resolution.nb_solutions}, la plus courte = {resolution.solution_la_plus_courte}")

    lot_de_plateaux.arret_des_enregistrements_de_difficultes_plateaux()
    for difficulte, liste_plateaux in lot_de_plateaux.difficulte_plateaux.items():
        # logger.info(f"*** Difficulté : {difficulte}")
        # logger.info(f"{' '*5}'{liste_plateaux}'")
        logger.info(f"*** Difficulté : {difficulte} - {len(liste_plateaux)} plateau{'x' if len(liste_plateaux) > 1 else ''}")
    logger.info('*'*80)


def main():
    profil = ProfilerLeCode('chercher_les_plateaux_et_les_solutions', PROFILER_LE_CODE)
    profil.start()

    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"chercher_en_parallele.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)

    for lignes in LIGNES:
        for colonnes in COLONNES:
            chercher_les_plateaux_et_les_solutions(colonnes, lignes)
    profil.stop()
    logger.info('-'*10 + " FIN " + '-'*10)

if __name__ == "__main__":
    main()
