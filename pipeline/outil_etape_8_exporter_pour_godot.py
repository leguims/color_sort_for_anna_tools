"""Crée un fichier qui rassemble tous les gameplays de GODOT avec leur attributs spécifiques."""
import logging
from pathlib import Path

import sys
import os

# pour importer depuis le dossier parent
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from io_utils.export_json import ExportJSON
from io_utils.chrono import Chrono

class ExporterLesSolutionsPourGodot:
    """Parcourt 'Solutions_classees.json' et crée un fichier de campagne pour Godot"""
    def __init__(self,
                repertoire_solution,
                fichier_solution_classique,
                fichier_solution_qui_perd_gagne,
                fichier_godot,
                nom_etape,
                fichier_journal):
        self._repertoire_solution = repertoire_solution
        self._fichier_solution_classique = fichier_solution_classique
        self._fichier_solution_qui_perd_gagne = fichier_solution_qui_perd_gagne
        self._fichier_godot = fichier_godot
        self._nom_etape = nom_etape
        self._fichier_journal = fichier_journal
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._chrono = Chrono()

    @property
    def elapsed(self):
        return self._chrono.elapsed

    def exporter_vers_godot(self):
        # Configurer le logger
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{self._nom_etape}")
        logger.info(f"DEBUT {self._nom_etape}")

        # Creation du fichier de campagne pour Godot
        solutions_godot = {"liste difficulte des plateaux": {}}
        liste_difficulte = solutions_godot["liste difficulte des plateaux"]

        # Rassembler les plateaux du gameplay avec ses attributs spécifiques
        solutions_classees_classique_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                                       nom_export=self._fichier_solution_classique,
                                                       repertoire=self._repertoire_solution)
        solutions_classees_classique = solutions_classees_classique_json.importer()

        self._chrono.start()
        if solutions_classees_classique.get('liste difficulte des plateaux'):
            for difficulte, liste_plateaux in solutions_classees_classique.get('liste difficulte des plateaux', {}).items():
                for plateau in liste_plateaux:
                    difficulte_json_key_str = f"{int(difficulte):03d}"
                    if difficulte_json_key_str not in liste_difficulte:
                        liste_difficulte[difficulte_json_key_str] = []
                    plateau_classique = {
                        "nom": plateau,
                        "difficulte": difficulte,
                        "gameplay": "CLASSIQUE"
                        }
                    liste_difficulte[difficulte_json_key_str].append(plateau_classique)
        self._chrono.pause()
        logger.info(f"Export des plateaux Classique achevé")

        solutions_classees_qui_perd_gagne_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                                       nom_export=self._fichier_solution_qui_perd_gagne,
                                                       repertoire=self._repertoire_solution)
        solutions_classees_qui_perd_gagne = solutions_classees_qui_perd_gagne_json.importer()

        self._chrono.start()
        if solutions_classees_qui_perd_gagne.get('liste difficulte des plateaux'):
            for difficulte, liste_plateaux in solutions_classees_qui_perd_gagne.get('liste difficulte des plateaux', {}).items():
                for plateau in liste_plateaux:
                    difficulte_json_key_str = f"{int(difficulte):03d}"
                    if difficulte_json_key_str not in liste_difficulte:
                        liste_difficulte[difficulte_json_key_str] = []
                    plateau_qui_perd_gagne = {
                        "nom": plateau,
                        "difficulte": difficulte,
                        "gameplay": "QUI_PERD_GAGNE"
                    }
                    liste_difficulte[difficulte_json_key_str].append(plateau_qui_perd_gagne)
        self._chrono.pause()
        logger.info(f"Export des plateaux Qui Perd Gagne achevé")

        logger.info(f"Traitement {self._nom_etape} en {self._chrono} secondes")

        export_godot_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                       nom_export=self._fichier_godot,
                                       repertoire=self._repertoire_solution)
        export_godot_json.effacer()
        export_godot_json.forcer_export(solutions_godot)
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
        fichier_solution_classique='7_filtrer_les_solutions_CLASSIQUE_pour_godot',
        fichier_solution_qui_perd_gagne='7_filtrer_les_solutions_QUI_PERD_GAGNE_pour_godot',
        fichier_godot='8_solutions_godot',
        nom_etape=NOM_ETAPE,
        fichier_journal=FICHIER_JOURNAL,
    )
    solutions_godot.exporter_vers_godot()
