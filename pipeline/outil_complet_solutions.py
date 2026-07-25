"Module pour créer, résoudre et qualifier les solutions des plateaux de 'ColorWoodSort'"
import logging
from pathlib import Path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # pour importer depuis le dossier parent

from pipeline.outil_complet import OutilComplet

if __name__ == "__main__":
    NOM_TACHE = 'outil_complet_solutions'
    FICHIER_JOURNAL = Path('..') / '..' / 'logs' / f'{NOM_TACHE}.log'
    REPERTOIRE_PIPELINE = Path('..') / '..' / 'Pipelines_rapide'

    # Chercher en boucle:
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"Synthese des solutions")
    logger.info('-'*10 + " DEBUT " + '-'*10)
    # La synthese des solutions s'applique à tous les plateaux disponibles.
    outil_complet = OutilComplet(
        liste_nb_colonnes=[1],
        liste_nb_lignes=[1],
        nb_colonnes_vides=1,
        repertoire_pipeline=REPERTOIRE_PIPELINE,
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL
    )
    outil_complet.export_godot()
    logger.info('-'*10 + " FIN " + '-'*10)
