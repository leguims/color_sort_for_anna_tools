"Module pour creer des plateaux de 'ColorWoodSort'"
import logging
from pathlib import Path

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # pour importer depuis le dossier parent

from core.plateau import Plateau
from core.lot_de_plateaux.iterator import IterPlateau
from io_utils.chrono import Chrono

class ChercherDesPlateaux:
    "Module pour creer des plateaux de 'ColorWoodSort'"
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                repertoire_analyse,
                nom_tache,
                fichier_journal,
                periode_affichage = 1*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse = repertoire_analyse
        self._nom_tache = nom_tache
        self._nom_etape = 'chercher_des_plateaux'
        self._fichier_journal = fichier_journal
        self._periode_affichage = periode_affichage

    def chercher_des_plateaux(self, colonnes, lignes):
        # Configurer le logger en doublon pour la paralelisation
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{colonnes}.{lignes}.{self._nom_etape}")
        logger.info(f"DEBUT {self._nom_etape}")
        lot_de_plateaux = IterPlateau((colonnes, lignes, self._nb_colonnes_vides))
        chrono = Chrono()
        chrono.start()
        for plateau in lot_de_plateaux:
            pass
        chrono.pause()
        logger.info(f"Traitement {self._nom_etape} en {chrono} secondes")
        logger.info(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
        logger.info(f"nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
        # liste_plateaux_valides = []
        # for plateau_ligne_texte in lot_de_plateaux.plateaux_valides:
        #     p = Plateau(colonnes, lignes, self._nb_colonnes_vides)
        #     p.plateau_ligne_texte = plateau_ligne_texte
        #     liste_plateaux_valides.append(p.plateau_ligne_texte_universel)
        #     # logger.info(f"plateau_ligne_texte_universel = '{p.plateau_ligne_texte_universel}'")
        # logger.info(f"liste plateaux = '{liste_plateaux_valides}'")
        
    def chercher_en_sequence(self):
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for iter_lignes in self._nb_lignes:
            for iter_colonnes in self._nb_colonnes:
                self.chercher_des_plateaux(iter_colonnes, iter_lignes)
        logger.info('-'*10 + " FIN " + '-'*10)

if __name__ == "__main__":
    NOM_TACHE = 'chercher_des_plateaux'
    FICHIER_JOURNAL = Path('..') / 'logs' / f'{NOM_TACHE}.log'
    FICHIER_ANALYSE = Path('..') / '..' / 'Pipelines' / 'pipeline_1_chercher_des_plateaux'

    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    chercher_plateaux = ChercherDesPlateaux(
        nb_colonnes=[3], #range(2, 12),
        nb_lignes=[3], #range(2, 14),
        nb_colonnes_vides=1,
        repertoire_analyse=str(FICHIER_ANALYSE),
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL
    )
    chercher_plateaux.chercher_en_sequence()
