"Module pour creer des plateaux de 'ColorWoodSort'"
import logging
from pathlib import Path

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # pour importer depuis le dossier parent

from core.lot_de_plateaux import LotDePlateaux
from io_utils.chrono import Chrono

class ChercherDesPlateaux:
    "Module pour creer des plateaux de 'ColorWoodSort'"
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                repertoire_analyse,
                repertoire_filtre,
                nom_tache,
                fichier_journal,
                periode_affichage = 1*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse = repertoire_analyse
        self._repertoire_filtre = repertoire_filtre
        self._nom_tache = nom_tache
        self._nom_etape = 'chercher_des_plateaux'
        self._fichier_journal = fichier_journal
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._periode_affichage = periode_affichage
        self._chrono = Chrono()

    @property
    def elapsed(self):
        return self._chrono.elapsed

    def chercher_des_plateaux(self, colonnes, lignes):
        # Configurer le logger en doublon pour la paralelisation
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{colonnes}.{lignes}.{self._nom_etape}")
        logger.info(f"DEBUT {self._nom_etape}")
        lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                repertoire_export_json=self._repertoire_analyse)

        if not lot_de_plateaux.est_deja_termine and lignes > 2:
            # Le lot actuel n'est pas terminé, s'appuyer sur son parent
            lot_de_plateaux_parent_filtre = LotDePlateaux((colonnes, lignes-1, self._nb_colonnes_vides),
                                                        repertoire_export_json=self._repertoire_filtre)
            if lot_de_plateaux_parent_filtre.est_deja_termine and lot_de_plateaux_parent_filtre._filtrer_doublons_permutation_jetons_piles:
                # Si le parent est termine et filtré, on le donne comme reference pour accelerer l'iterateur
                lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                    repertoire_export_json=self._repertoire_analyse,
                                    parent_filtre=lot_de_plateaux_parent_filtre)
            else:
                lot_de_plateaux_parent_filtre = None

        self._chrono.start()
        for plateau in lot_de_plateaux:
            pass
        self._chrono.pause()
        logger.info(f"Traitement {self._nom_etape} en {self._chrono} secondes")
        logger.info(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
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
    FICHIER_FILTRE = Path('..') / '..' / 'Pipelines' / 'pipeline_5_filtre_doublons_permutation_jetons_piles'

    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    chercher_plateaux = ChercherDesPlateaux(
        nb_colonnes=[3], #range(2, 12),
        nb_lignes=[3], #range(2, 14),
        nb_colonnes_vides=1,
        repertoire_analyse=str(FICHIER_ANALYSE),
        repertoire_filtre=str(FICHIER_FILTRE),
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL
    )
    chercher_plateaux.chercher_en_sequence()
