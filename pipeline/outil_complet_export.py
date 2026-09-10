"Module pour créer, résoudre et qualifier les solutions des plateaux de 'ColorWoodSort'"
import logging
from pathlib import Path

import sys
import os
# pour importer depuis le dossier parent
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from pipeline.outil_complet import OutilComplet

if __name__ == "__main__":
    NOM_TACHE = 'outil_complet_export'
    FICHIER_JOURNAL = Path('..') / '..' / 'logs' / f'{NOM_TACHE}.log'
    REPERTOIRE_PIPELINE = Path('..') / '..' / 'Pipelines'

    PROFILER_LE_CODE = False

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
