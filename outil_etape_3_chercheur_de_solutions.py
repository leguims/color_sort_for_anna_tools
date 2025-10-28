"Parcourt les plateaux exhaustifs et en trouve les solutions 'ColorWoodSort'"
import datetime
import time
import logging
import pathlib

from plateau import Plateau
from lot_de_plateaux import LotDePlateaux
from resoudre_plateau import ResoudrePlateau
from profiler_le_code import ProfilerLeCode

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
        self._fichier_journal = fichier_journal
        self._memoire_max = memoire_max
        self._profiler_le_code = profiler_le_code
        self._periode_scrutation_secondes = periode_scrutation_secondes
        self._periode_affichage = periode_affichage

    def chercher_des_solutions(self, colonnes, lignes, taciturne=False):
        # Configurer le logger
        logger = logging.getLogger(f"{colonnes}.{lignes}.{self._nom_tache}")
        if not taciturne:
            logger.info(f"DEBUT")

        plateau = Plateau(colonnes, lignes, self._nb_colonnes_vides)
        lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse,
                                        nb_plateaux_max = self._memoire_max)
        if lot_de_plateaux.est_deja_termine(): # or True: # True = Chercher toutes les solutions a l'heure actuel.
            if not taciturne:
                logger.info("Ce lot de plateaux est termine")

            if lot_de_plateaux.nb_plateaux_valides != lot_de_plateaux.nb_plateaux_solutionnes:
                if lot_de_plateaux.nb_plateaux_valides < lot_de_plateaux.nb_plateaux_solutionnes:
                    logger.info(f"Il y a plus de plateaux de solutions que de plateaux valides ! Il y a un probleme ! {lot_de_plateaux.nb_plateaux_solutionnes} > {lot_de_plateaux.nb_plateaux_valides}")
                    # TODO : Il y a probablement des solutions de plateau obsoletes a effacer.
                logger.info(f"Il reste des solutions a trouver : {lot_de_plateaux.nb_plateaux_valides} != {lot_de_plateaux.nb_plateaux_solutionnes}")
                
                dernier_affichage  = datetime.datetime.now().timestamp() - self._periode_affichage
                nb_solutions_a_trouver = lot_de_plateaux.nb_plateaux_valides
                for plateau_ligne_texte_a_resoudre in lot_de_plateaux.plateaux_valides:
                    plateau.clear()
                    plateau.plateau_ligne_texte = plateau_ligne_texte_a_resoudre
                    if not lot_de_plateaux.est_deja_connu_difficulte_plateau(plateau):
                        resolution = ResoudrePlateau(plateau,
                                                    repertoire_analyse=self._repertoire_analyse,
                                                    repertoire_solution=self._repertoire_solution)
                        resolution.backtracking()
                        lot_de_plateaux.definir_difficulte_plateau(plateau, resolution.difficulte, len(resolution))
                    
                    # Afficher si dernier affichage > 5mins
                    nb_solutions_a_trouver -= 1
                    if datetime.datetime.now().timestamp() - dernier_affichage > self._periode_affichage:
                        logger.info(f"Il reste {nb_solutions_a_trouver} solutions a resoudre.")
                        dernier_affichage  = datetime.datetime.now().timestamp()

                lot_de_plateaux.arret_des_enregistrements_de_difficultes_plateaux()
                for difficulte, dico_nb_coups in lot_de_plateaux.difficulte_plateaux.items():
                    for nb_coups, liste_plateaux in dico_nb_coups.items():
                        logger.info(f"Difficulte : {difficulte} en {nb_coups} coups : {len(liste_plateaux)} plateau{self.pluriel(liste_plateaux, lettre='x')}")
            else:
                if not taciturne:
                    logger.info("Toutes les solutions sont trouvees.")
        else:
            if not taciturne:
                logger.info("Ce lot de plateaux n'est pas encore termine, pas de recherche de solution.")

    def pluriel(self, LIGNES, lettre='s'):
        return lettre if len(LIGNES) > 1 else ""

    def chercher_en_boucle(self):
        logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")

        logger.info('-'*10 + " 1ere RECHERCHE " + '-'*10)
        self.chercher_en_sequence() # 1ere iteration est bavarde
        while(True):
            logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
            for iter_lignes in self._nb_lignes:
                for iter_colonnes in self._nb_colonnes:
                    self.chercher_des_solutions(iter_colonnes, iter_lignes, taciturne=True)
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            logger.info(f"{current_time} - Attente entre 2 iterations de {self._periode_scrutation_secondes}s...")
            time.sleep(self._periode_scrutation_secondes)

    def chercher_en_sequence(self):
        profil = ProfilerLeCode('chercher_des_solutions', self._profiler_le_code)
        profil.start()

        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for iter_lignes in self._nb_lignes:
            for iter_colonnes in self._nb_colonnes:
                self.chercher_des_solutions(iter_colonnes, iter_lignes)
        profil.stop()

if __name__ == "__main__":
    NOM_TACHE = 'chercher_des_solutions'
    FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

    # Configurer le logger
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    chercher_solutions = ChercherDesSolutions(
        nb_colonnes=[3], #range(2, 12) #[2] # range(2, 5) # range(2, 5) #11
        nb_lignes=[4], #range(2,6) #[5] #range(2,6) #range(2, 14) #[3] # [2,3] #4
        nb_colonnes_vides=1,
        repertoire_analyse='Analyse_nouvelle_architecture',
        repertoire_solution='Solutions_nouvelle_architecture',
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL
    )
    # chercher_solutions.chercher_en_parallele()
    chercher_solutions.chercher_en_sequence()
