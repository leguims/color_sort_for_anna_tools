"Module pour creer des plateaux de 'ColorWoodSort'"
import logging
from pathlib import Path

import sys
import os
import random

# pour importer depuis le dossier parent
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from core.lot_de_plateaux import LotDePlateaux
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
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._periode_affichage = periode_affichage
        self._chrono = Chrono()
        self._done = False

    @property
    def elapsed(self):
        return self._chrono.elapsed

    @property
    def done(self):
        return self._done

    def chercher_des_plateaux(self, colonnes, lignes):
        # Configurer le logger en doublon pour la paralelisation
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{colonnes}.{lignes}.{self._nom_etape}")
        logger.info(f"DEBUT {self._nom_etape}")
        lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                repertoire_export_json=self._repertoire_analyse)
        self._chrono.start()
        for plateau in lot_de_plateaux:
            pass
        self._chrono.pause()
        self._done = True
        logger.info(f"Traitement {self._nom_etape} en {self._chrono} secondes")
        logger.info(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
        
    def chercher_en_sequence(self):
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        # Parcourir aléatoirement pour pouvoir lancer plusieurs scripts en parallele san conflit de fichiers.
        liste_colonne_ligne = [{'colonnes':c, 'lignes':l} for c in self._nb_colonnes for l in self._nb_lignes]
        random.shuffle(liste_colonne_ligne)
        for colonne_ligne in liste_colonne_ligne:
            self.chercher_des_plateaux(colonne_ligne.get('colonnes'), colonne_ligne.get('lignes'))
        logger.info('-'*10 + " FIN " + '-'*10)

if __name__ == "__main__":
    NOM_TACHE = 'chercher_des_plateaux'
    FICHIER_JOURNAL = Path('..') / 'logs' / f'{NOM_TACHE}.log'
    FICHIER_ANALYSE = Path('..') / '..' / 'Pipelines' / 'pipeline_1_chercher_des_plateaux'

    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
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
