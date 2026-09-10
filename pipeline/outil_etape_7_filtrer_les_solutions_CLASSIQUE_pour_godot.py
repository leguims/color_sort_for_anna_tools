"""Parcourt les plateaux resolus et les rassemble par GAMEPLAY dans un fichier dédié.
Les plateaux sont dans une écriture universelle avec les attributs spécifiques liés au GAMEPLAY.
Entrée : 'pipeline_5_filtre_doublons_permutation_jetons_piles'
Entrée : 'pipeline_6_solutions_unitaires'
Sortie : '7_filtrer_les_solutions_CLASSIQUE_pour_godot'"""

import datetime
import time
import logging
from pathlib import Path

import sys

# Allow this script to run directly from any working directory.
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from core.plateau import Plateau
from core.lot_de_plateaux import LotDePlateaux
from core.resoudre_plateau import ResoudrePlateau
from io_utils.profiler_le_code import ProfilerLeCode
from io_utils.export_json import ExportJSON
from io_utils.chrono import Chrono

class FiltrerLesSolutionsClassique:
    """Parcourt les plateaux resolus et les rassemble dans le fichier
    'Solutions_classees.json' par difficulte avec une ecriture universelle"""
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                repertoire_analyse,
                repertoire_solution_unitaire,
                repertoire_solution,
                fichier_solution,
                nb_coups_min,
                difficulte_min,
                difficulte_max,
                nb_chemins_min,
                nom_tache,
                fichier_journal,
                profiler_le_code = False,
                periode_scrutation_secondes = 30*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse = repertoire_analyse
        self._repertoire_solution_unitaire = repertoire_solution_unitaire
        self._repertoire_solution = repertoire_solution
        self._fichier_solution = fichier_solution
        self._nb_coups_min = nb_coups_min
        self._difficulte_min = difficulte_min
        self._difficulte_max = difficulte_max
        self._nb_chemins_min = nb_chemins_min
        self._nom_tache = nom_tache
        self._fichier_journal = fichier_journal
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._profiler_le_code = profiler_le_code
        self._periode_scrutation_secondes = periode_scrutation_secondes
        self._chrono = Chrono()

    @property
    def elapsed(self):
        return self._chrono.elapsed

    def classer_les_solutions(self, colonnes, lignes):
        # Configurer le logger
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{colonnes}.{lignes}.{self._nom_tache}")
        logger.info(f"DEBUT {self._nom_tache}")
        # logger.info(plateau.plateau_ligne_texte_universel)
        plateau = Plateau(colonnes, lignes, self._nb_colonnes_vides)
        lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse)
        if lot_de_plateaux.est_deja_termine:
            logger.info("Ce lot de plateaux est termine")

            logger.info("Importer les solutions CLASSIQUE")
            solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=self._fichier_solution, repertoire=self._repertoire_solution)
            solutions_classees = solutions_classees_json.importer()
            plateau = Plateau(colonnes, lignes, self._nb_colonnes_vides)

            if "liste difficulte des plateaux" not in solutions_classees:
                solutions_classees["liste difficulte des plateaux"] = {}
            dict_difficulte = solutions_classees["liste difficulte des plateaux"]

            # Parcourir chaque solution et remplir la structure de données
            for plateau_ligne_texte_a_filtrer in lot_de_plateaux.plateaux_valides:
                plateau.clear()
                plateau.plateau_ligne_texte = plateau_ligne_texte_a_filtrer
                plateau_ligne_texte_universel = plateau.plateau_ligne_texte_universel
                # Consulter la résolution du plateau
                self._chrono.start()
                resolution = ResoudrePlateau(plateau,
                                            repertoire_solution=self._repertoire_solution_unitaire)
                difficulte = resolution.difficulte_classique
                lg_solution = resolution.longueur_solution_classique
                nb_chemins = resolution.nb_chemins
                # Filtrage des plateaux selon la qualité des solutions
                if self._difficulte_min <= difficulte <= self._difficulte_max \
                    and lg_solution >= self._nb_coups_min \
                    and nb_chemins >= self._nb_chemins_min:
                    if difficulte not in dict_difficulte:
                        dict_difficulte[difficulte] = []
                    if plateau_ligne_texte_universel not in dict_difficulte[difficulte]:
                        dict_difficulte[difficulte].append(plateau_ligne_texte_universel)
                self._chrono.pause()
            logger.info(f"Traitement {self._nom_tache} en {self._chrono} secondes")
            logger.info("Filtrage des solutions CLASSIQUE")
            self.ordonner_difficulte(solutions_classees["liste difficulte des plateaux"])
            solutions_classees_json.forcer_export(solutions_classees)
            logger.info("Export termine")
        else:
            logger.info(" - Ce lot de plateaux n'est pas encore termine, pas de classement de solutions.")

    # Copie de 'LotDePlateaux.arret_des_enregistrements_de_difficultes_plateaux()'
    def ordonner_difficulte(self, ensemble_des_difficultes_de_plateaux):
        "Methode qui classe les difficultes des solutions"
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

    def afficher_synthese(self):
        logger = logging.getLogger(f"chercher.afficher_synthese")
        logger.info(f"*** Synthese des Solutions CLASSIQUE:")
        solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=self._fichier_solution, repertoire=self._repertoire_solution)
        solutions_classees = solutions_classees_json.importer()

        somme_plateaux = 0
        if solutions_classees.get('liste difficulte des plateaux'):
            for difficulte, liste_plateaux in solutions_classees.get('liste difficulte des plateaux', {}).items():
                logger.info(f" - Difficulte : {difficulte} : {len(liste_plateaux)} plateau{self.pluriel(liste_plateaux, 'x')}")
                if difficulte:
                    somme_plateaux += len(liste_plateaux)
            logger.info(f" - Total : {somme_plateaux} plateau{self.pluriel(range(somme_plateaux), 'x')} valide{self.pluriel(range(somme_plateaux), 's')}")

    def pluriel(self, LIGNES, lettre='s'):
        return lettre if len(LIGNES) > 1 else ""

    def chercher_en_boucle(self):
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")

        while(True):
            logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
            for iter_lignes in self._nb_lignes:
                for iter_colonnes in self._nb_colonnes:
                    self.classer_les_solutions(iter_colonnes, iter_lignes)
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            logger.info(f"{current_time} - Attente entre 2 iterations de {self._periode_scrutation_secondes}s...")
            time.sleep(self._periode_scrutation_secondes)

    def chercher_en_sequence(self):
        profil = ProfilerLeCode('chercher_des_solutions', self._profiler_le_code)
        profil.start()

        # Effacer l'existant
        solutions_classees_json = ExportJSON(0, 0, '', nom_export=self._fichier_solution, repertoire=self._repertoire_solution)
        solutions_classees_json.effacer()
        
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for iter_lignes in self._nb_lignes:
            for iter_colonnes in self._nb_colonnes:
                self.classer_les_solutions(iter_colonnes, iter_lignes)
        profil.stop()

        self.afficher_synthese()
        logger.info('-'*10 + " FIN " + '-'*10)

if __name__ == "__main__":
    NOM_TACHE = 'classer_les_solutions_classique'
    FICHIER_JOURNAL = Path('..') / '..' /'logs' / f'{NOM_TACHE}.log'
    FICHIER_ANALYSE = Path('..') / '..' / 'Pipelines' / 'pipeline_5_filtre_doublons_permutation_jetons_piles'
    FICHIER_SOLUTION_UNITAIRE = Path('..') / '..' / 'Pipelines' / 'pipeline_6_solutions_unitaires'
    FICHIER_SOLUTION = Path('..') / '..' / 'Pipelines' / 'pipeline_6_solutions'

    # Configurer le logger
    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    classer_solutions = FiltrerLesSolutionsClassique(
        nb_colonnes=[3], #range(2, 12),
        nb_lignes=[5], #range(2, 14),
        nb_colonnes_vides=1,
        repertoire_analyse=str(FICHIER_ANALYSE),
        repertoire_solution_unitaire=str(FICHIER_SOLUTION_UNITAIRE),
        repertoire_solution=str(FICHIER_SOLUTION),
        fichier_solution='7_filtrer_les_solutions_CLASSIQUE_pour_godot',
        nb_coups_min=3,
        difficulte_min=1,
        difficulte_max=99,
        nb_chemins_min=10,
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL,
        periode_scrutation_secondes = 1 * 60 * 60 # 1h
    )
    classer_solutions.chercher_en_sequence()
    #classer_solutions.chercher_en_boucle()
