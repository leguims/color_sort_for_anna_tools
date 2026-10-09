"""Parcourt les plateaux resolus et les rassemble par GAMEPLAY dans un fichier dédié.
Les plateaux sont dans une écriture universelle avec les attributs spécifiques liés au GAMEPLAY.
Entrée : 'pipeline_5_filtre_doublons_permutation_jetons_piles'
Entrée : 'pipeline_6_solutions_unitaires'
Sortie : '7_filtrer_les_solutions_QUI_PERD_GAGNE_pour_godot'"""

import logging
from pathlib import Path

import sys
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from core.plateau import Plateau
from core.lot_de_plateaux import LotDePlateaux
from core.resoudre_plateau import ResoudrePlateau
from io_utils.export_json import ExportJSON

from pipeline.outil_etape_8_filtrer_les_solutions_CLASSIQUE_pour_godot import FiltrerLesSolutionsClassique

class FiltrerLesSolutionsQuiPerdGagne(FiltrerLesSolutionsClassique):
    """Parcourt les plateaux resolus et les rassemble dans le fichier
    'Solutions_classees.json' par difficulte avec une ecriture universelle"""


if __name__ == "__main__":
    NOM_TACHE = 'classer_les_solutions_qui_perd_gagne'
    NOM_DEPOT = 'color_sort_for_anna_tools'
    if Path().parent.resolve().name == NOM_DEPOT:
        # DEBUG
        FICHIER_JOURNAL = Path('logs') / f'{NOM_TACHE}.log'
        FICHIER_ANALYSE = Path('Pipelines') / 'pipeline_6_fusion_filtre_doublons_permutation_jetons_piles'
        FICHIER_SOLUTION_UNITAIRE = Path('Pipelines') / 'pipeline_7_solutions_unitaires'
        FICHIER_SOLUTION = Path('Pipelines') / 'pipeline_7_solutions'
    elif Path().parent.resolve().name == (Path(NOM_DEPOT) / 'sources' / 'pipeline').name:
        FICHIER_JOURNAL = Path('..') / '..' / 'logs' / f'{NOM_TACHE}.log'
        FICHIER_ANALYSE = Path('..') / '..' / 'Pipelines' / 'pipeline_6_fusion_filtre_doublons_permutation_jetons_piles'
        FICHIER_SOLUTION_UNITAIRE = Path('..') / '..' / 'Pipelines' / 'pipeline_7_solutions_unitaires'
        FICHIER_SOLUTION = Path('..') / '..' / 'Pipelines' / 'pipeline_7_solutions'
    else:
        print("Impossible de déterminer le chemin des fichiers en mode debug ou release.")
        exit(1)

    # Configurer le logger
    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    classer_solutions = FiltrerLesSolutionsQuiPerdGagne(
        nb_colonnes=range(2, 12),
        nb_lignes=range(2, 14),
        nb_colonnes_vides=1,
        gameplay='QUI_PERD_GAGNE',
        repertoire_analyse=str(FICHIER_ANALYSE),
        repertoire_solution_unitaire=str(FICHIER_SOLUTION_UNITAIRE),
        repertoire_solution=str(FICHIER_SOLUTION),
        nb_coups_min=3,
        difficulte_min=1,
        difficulte_max=99,
        nb_chemins_min=10,
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL,
        periode_scrutation_secondes = 1 * 60 * 60 # 1h
    )
    classer_solutions.chercher_en_sequence()
    # classer_solutions.afficher_enregistrer_synthese()
    #classer_solutions.chercher_en_boucle()
