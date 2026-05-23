"""Tronque le fichier de solutions GODOT"""
import logging
from pathlib import Path
import random

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # pour importer depuis le dossier parent

from io_utils.export_json import ExportJSON
from io_utils.chrono import Chrono

class TronquerLesSolutionsGodot:
    """Decoupe l'ensemble des solutions inter-plateaux en des ensembles plus petits de solutions
    Adapte pour avoir un fichier de solutions restreint pour le jeu"""
    def __init__(self,
                repertoire_solution,
                fichier_godot,
                fichier_godot_tronque,
                nombre_de_plateaux: int,
                nom_etape,
                fichier_journal):
        self._repertoire_solution = repertoire_solution
        self._fichier_godot = fichier_godot
        self._fichier_godot_tronque = fichier_godot_tronque
        self._nombre_de_plateaux: int = nombre_de_plateaux
        self._nom_etape = nom_etape
        self._fichier_journal = fichier_journal
        self._chrono = Chrono()

    def tronquer(self):
        # Configurer le logger
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{self._nom_etape}")
        logger.info(f"*** Tronquer les solutions GODOT")

        solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                nom_export=self._fichier_godot, repertoire=self._repertoire_solution)
        solutions_classees = solutions_classees_json.importer()
        solutions_classees_tronquees_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                nom_export=self._fichier_godot_tronque, repertoire=self._repertoire_solution)

        if "liste difficulte des plateaux" in solutions_classees:
            dict_difficulte: dict[str, list] = solutions_classees.get("liste difficulte des plateaux")
            
            # Rationnaliser l'objectif de plateaux
            nb_plateaux_total = 0
            for v in dict_difficulte.values():
                nb_plateaux_total += len(v)
            self._nombre_de_plateaux = min(nb_plateaux_total, self._nombre_de_plateaux)

            solutions_classees_tronques = {"liste difficulte des plateaux": {}}
            dict_difficulte_tronque = solutions_classees_tronques['liste difficulte des plateaux']

            self._chrono.start()
            while self._nombre_de_plateaux:
                for difficulte, liste_plateaux in dict_difficulte.items():
                    if difficulte not in dict_difficulte_tronque:
                        dict_difficulte_tronque[difficulte] = []
                    # print(liste_plateaux)
                    # TODO : Attention s'il n'y a pas assez de plateaux !
                    plateau_aleatoire = random.choice(liste_plateaux)
                    if plateau_aleatoire not in dict_difficulte_tronque[difficulte]:
                        dict_difficulte_tronque[difficulte].append(plateau_aleatoire)
                        self._nombre_de_plateaux -= 1
                    if not self._nombre_de_plateaux:
                        break
            self._chrono.pause()
            logger.info(f"Traitement {self._nom_etape} en {self._chrono} secondes")
            solutions_classees_tronquees_json.effacer()
            solutions_classees_tronquees_json.forcer_export(solutions_classees_tronques)
            logger.info(f"Tronquage termine")
        else:
            logger.info("Aucune solution trouvee dans le fichier de solutions GODOT")

if __name__ == "__main__":
    NOM_ETAPE = 'tronquer_les_solutions_godot'
    FICHIER_JOURNAL = Path('..') / 'logs' / f'{NOM_ETAPE}.log'
    FICHIER_SOLUTION = Path('..') / '..' / 'Pipelines' / 'pipeline_6_solutions'

    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    tronquer_godot = TronquerLesSolutionsGodot(
        repertoire_solution=str(FICHIER_SOLUTION),
        fichier_godot='8_exporter_pour_godot_Solutions_classees',
        fichier_godot_tronque='9_tronquer_les_solutions_godot',
        nombre_de_plateaux=200,
        nom_etape=NOM_ETAPE,
        fichier_journal=FICHIER_JOURNAL
    )
    tronquer_godot.tronquer()
