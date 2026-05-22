"""Crée un fichier directement intégrable dans la production GODOT."""
import logging
from pathlib import Path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # pour importer depuis le dossier parent

from io_utils.export_json import ExportJSON
from io_utils.chrono import Chrono

class ExporterLesSolutionsPourGodot:
    """Parcourt 'Solutions_classees.json' et supprime la notion de nombre de coups"""
    def __init__(self,
                repertoire_solution,
                fichier_solution,
                fichier_godot,
                nom_etape,
                fichier_journal,
                periode_scrutation_secondes = 30*60): # en secondes
        self._repertoire_solution = repertoire_solution
        self._fichier_solution = fichier_solution
        self._fichier_godot = fichier_godot
        self._nom_etape = nom_etape
        self._fichier_journal = fichier_journal
        self._periode_scrutation_secondes = periode_scrutation_secondes

    def exporter_vers_godot(self):
        # Configurer le logger
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{self._nom_etape}")
        logger.info(f"DEBUT {self._nom_etape}")
        solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=self._fichier_solution, repertoire=self._repertoire_solution)
        solutions_classees = solutions_classees_json.importer()

        # Creation du fichier de solution pour Godot
        solution_godot = {"liste difficulte des plateaux": {}}
        chrono = Chrono()
        chrono.start()
        for difficulte, dico_nb_coups in solutions_classees.get('liste difficulte des plateaux').items():
            for nb_coups, liste_plateaux in dico_nb_coups.items():
                if str(difficulte) not in solution_godot["liste difficulte des plateaux"]:
                    solution_godot["liste difficulte des plateaux"][str(difficulte)] = []
                solution_godot["liste difficulte des plateaux"][str(difficulte)] += liste_plateaux
        chrono.pause()
        logger.info(f"Traitement {self._nom_etape} en {chrono} secondes")
        export_godot_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=self._fichier_godot, repertoire=self._repertoire_solution)
        export_godot_json.effacer()
        export_godot_json.forcer_export(solution_godot)
        logger.info("Export termine")


if __name__ == "__main__":
    NOM_ETAPE = 'exporter_vers_godot'
    FICHIER_JOURNAL = Path('..') / 'logs' / f'{NOM_ETAPE}.log'
    FICHIER_SOLUTION = Path('..') / '..' / 'Pipelines' / 'pipeline_6_solutions'

    # Configurer le logger
    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    solutions_godot = ExporterLesSolutionsPourGodot(
        repertoire_solution=str(FICHIER_SOLUTION),
        fichier_solution='7_filtrer_les_solutions_pour_godot',
        fichier_godot='8_exporter_pour_godot_Solutions_classees',
        nom_etape=NOM_ETAPE,
        fichier_journal=FICHIER_JOURNAL,
        periode_scrutation_secondes = 1 * 60 * 60 # 1h
    )
    solutions_godot.exporter_vers_godot()
