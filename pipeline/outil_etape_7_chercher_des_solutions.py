"Parcourt les plateaux exhaustifs et en trouve les solutions 'ColorWoodSort'"
import copy
import datetime
import time
import logging
from pathlib import Path
import random

import sys

# pour importer depuis le dossier parent
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from core.plateau import Plateau
from core.lot_de_plateaux import LotDePlateaux
from core.resoudre_plateau import ResoudrePlateau
from io_utils.profiler_le_code import ProfilerLeCode
from io_utils.chrono import Chrono

class ChercherDesSolutions:
    "Parcourt les plateaux exhaustifs et en trouve les solutions 'ColorWoodSort'"
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                repertoire_analyse,
                repertoire_solution,
                nom_tache,
                fichier_journal,
                memoire_max = 5_000_000,
                profiler_le_code = False,
                periode_scrutation_secondes = 30*60, # en secondes
                periode_affichage = 1*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse = repertoire_analyse
        self._repertoire_solution = repertoire_solution
        self._nom_tache = nom_tache
        self._nom_etape = 'chercher_des_solutions'
        self._fichier_journal = fichier_journal
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._memoire_max = memoire_max
        self._profiler_le_code = profiler_le_code
        self._periode_scrutation_secondes = periode_scrutation_secondes
        self._periode_affichage = periode_affichage
        self._chrono = Chrono()
        self._done = False

    @property
    def elapsed(self):
        return self._chrono.elapsed

    @property
    def done(self):
        return self._done

    def creer_repertoire_solution(self):
        # Crée le repertoire pour la synthèse des solutions
        if not (self._repertoire_solution).exists():
            self._repertoire_solution.mkdir(parents=True, exist_ok=True)

    def chercher_des_solutions(self, colonnes, lignes):
        # Configurer le logger
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{colonnes}.{lignes}.{self._nom_etape}")
        # logger.info(f"DEBUT {self._nom_etape}")

        lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse,
                                        nb_plateaux_max = self._memoire_max)
        if lot_de_plateaux.est_deja_termine:
            self.creer_repertoire_solution()
            plateau = Plateau(colonnes, lignes, self._nb_colonnes_vides)

            if lot_de_plateaux.nb_plateaux_valides != lot_de_plateaux.nb_plateaux_solutionnes:
                if lot_de_plateaux.nb_plateaux_valides < lot_de_plateaux.nb_plateaux_solutionnes:
                    logger.error(f"Il y a plus de plateaux de solutions que de plateaux valides ! Il y a un probleme ! {lot_de_plateaux.nb_plateaux_solutionnes} > {lot_de_plateaux.nb_plateaux_valides}")
                    # TODO : Il y a probablement des solutions de plateau obsoletes a effacer.
                logger.info(f"Il reste des solutions a trouver : {lot_de_plateaux.nb_plateaux_valides} != {lot_de_plateaux.nb_plateaux_solutionnes}")

                dernier_affichage  = datetime.datetime.now().timestamp() - self._periode_affichage
                nb_solutions_a_trouver = lot_de_plateaux.nb_plateaux_valides
                lot_de_plateaux.reset_solutions()
                plateaux_valides_melanges = list(copy.deepcopy(lot_de_plateaux.plateaux_valides))
                random.shuffle(plateaux_valides_melanges)
                for plateau_ligne_texte_a_resoudre in plateaux_valides_melanges:
                    plateau.clear()
                    plateau.plateau_ligne_texte = plateau_ligne_texte_a_resoudre
                    self._chrono.start()
                    resolution = ResoudrePlateau(plateau,
                                                repertoire_solution=self._repertoire_solution)
                    resolution.backtracking()
                    self._chrono.pause()
                    lot_de_plateaux.incrementer_nb_solutions()
                    
                    # Afficher si dernier affichage > 5mins
                    nb_solutions_a_trouver -= 1
                    if datetime.datetime.now().timestamp() - dernier_affichage > self._periode_affichage:
                        logger.info(f"Il reste {nb_solutions_a_trouver} solutions a resoudre.")
                        dernier_affichage  = datetime.datetime.now().timestamp()
                logger.info(f"Traitement {self._nom_etape} en {self._chrono} secondes")

                lot_de_plateaux.arret_des_enregistrements_de_difficultes_plateaux()
                self._done = True
            else:
                self._done = False
                logger.info("Toutes les solutions sont trouvees.")
        else:
            self._done = False
            logger.info("Ce lot de plateaux n'est pas encore termine, pas de recherche de solution.")
        # logger.info(f"FIN {self._nom_etape}")

    def chercher_en_boucle(self):
        logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")

        logger.info('-'*10 + " 1ere RECHERCHE " + '-'*10)
        self.chercher_en_sequence() # 1ere iteration est bavarde
        while(True):
            # logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
            liste_colonne_ligne = [{'colonnes':c, 'lignes':l} for c in self._nb_colonnes for l in self._nb_lignes]
            random.shuffle(liste_colonne_ligne)
            for colonne_ligne in liste_colonne_ligne:
                self.chercher_des_solutions(colonne_ligne.get('colonnes'), colonne_ligne.get('lignes'))
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            logger.info(f"{current_time} - Attente entre 2 iterations de {self._periode_scrutation_secondes}s...")
            time.sleep(self._periode_scrutation_secondes)

    def chercher_en_sequence(self):
        profil = ProfilerLeCode('chercher_des_solutions', self._profiler_le_code)
        profil.start()

        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        # logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        # Parcourir aléatoirement pour pouvoir lancer plusieurs solutions en parallele.
        liste_colonne_ligne = [{'colonnes':c, 'lignes':l} for c in self._nb_colonnes for l in self._nb_lignes]
        random.shuffle(liste_colonne_ligne)
        for colonne_ligne in liste_colonne_ligne:
            self.chercher_des_solutions(colonne_ligne.get('colonnes'), colonne_ligne.get('lignes'))
        # logger.info('-'*10 + " FIN " + '-'*10)
        profil.stop()

if __name__ == "__main__":
    NOM_TACHE = 'chercher_des_solutions'
    FICHIER_JOURNAL = Path('..') / 'logs' / f'{NOM_TACHE}.log'
    REPERTOIRE_ANALYSE = Path('..') / '..' / 'Pipelines' / 'pipeline_6_fusion_filtre_doublons_permutation_jetons_piles'
    REPERTOIRE_SOLUTION = Path('..') / '..' / 'Pipelines' / 'pipeline_7_solutions_unitaires'

    # Configurer le logger
    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    chercher_solutions = ChercherDesSolutions(
        nb_colonnes=[3], #range(2, 12),
        nb_lignes=[3], #range(2, 14),
        nb_colonnes_vides=1,
        repertoire_analyse=str(REPERTOIRE_ANALYSE),
        repertoire_solution=str(REPERTOIRE_SOLUTION),
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL,
        periode_scrutation_secondes = 1 * 60 * 60 # 1h
    )
    # chercher_solutions.chercher_en_parallele()
    chercher_solutions.chercher_en_sequence()
    # chercher_solutions.chercher_en_boucle()
