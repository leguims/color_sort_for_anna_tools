"Parcourt les plateaux et pratique un elagage des doublons et de similarite"
import datetime
import time
import logging
from pathlib import Path
import shutil
import random

import sys
import os
# pour importer depuis le dossier parent
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from core.lot_de_plateaux import LotDePlateaux
from io_utils.profiler_le_code import ProfilerLeCode
from io_utils.creer_les_taches import CreerLesTaches
from io_utils.chrono import Chrono

# TODO : Etape 1 à 5 à ajuster avec un parametre sur le type d'ITERATEUR (old ou RAPIDE)
#        ... + varier le chemin de sortie en fonction.

class FusionnerFiltrerLesPlateaux:
    "Parcourt les plateaux et pratique un elagage des doublons et de similarite"
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                repertoire_analyse_1,
                repertoire_analyse_2,
                repertoire_filtre,
                nom_tache,
                fichier_journal,
                memoire_max = 5_000_000,
                profiler_le_code = False,
                periode_scrutation_secondes = 30*60, # en secondes
                periode_affichage = 1*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse_1 = repertoire_analyse_1
        self._repertoire_analyse_2 = repertoire_analyse_2
        self._repertoire_filtre = repertoire_filtre
        self._nom_tache = nom_tache
        self._nom_etape = 'filtrer_doublons_permutation_jetons_piles'
        self._fichier_journal = fichier_journal
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._memoire_max = memoire_max
        self._profiler_le_code = profiler_le_code
        self._periode_scrutation_secondes = periode_scrutation_secondes
        self._periode_affichage = periode_affichage
        self._chrono = Chrono()
        self._done = False

    @property
    def elapsed(self):
        return self._chrono.elapsed

    @property
    def done(self):
        return self._done

    def copier_parent(self, source: Path, nb_colonnes, nb_lignes, reset_filtre=True):
        # Copie le repertoire 'Plateaux_XX_YY' et le fichier JSON
        destination = Path(self._repertoire_filtre) / source.parent.name
        if source.exists() and not (destination/source.name).exists():
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, destination)

            if reset_filtre:
                # Reset le filtrage pour la fusion à venir
                lot_de_plateaux = LotDePlateaux((nb_colonnes, nb_lignes, self._nb_colonnes_vides),
                                repertoire_export_json=self._repertoire_filtre)
                lot_de_plateaux._filtrer_doublons_permutation_jetons_piles = False
                lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)

    def filtrer_les_plateaux(self, nb_colonnes, nb_lignes):
        # Configurer le logger en doublon pour la paralelisation
        logging.basicConfig(filename=self._fichier_journal, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{nb_colonnes}.{nb_lignes}.{self._nom_etape}")
        # logger.info(f"DEBUT {self._nom_etape}")

        # TODO : Prevoir de créer un lien symbolique de PARENT_1 si PARENT_2 est vide.

        # Les 2 parents existent, le filtrage doit etre réalisé
        lot_de_plateaux_parent_1 = LotDePlateaux((nb_colonnes, nb_lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse_1,
                                        nb_plateaux_max = self._memoire_max)
        lot_de_plateaux_parent_2 = LotDePlateaux((nb_colonnes, nb_lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse_2,
                                        nb_plateaux_max = self._memoire_max)

        # Si l'un des parents est absent : copier le parent et ne pas réaliser le filtrage
        if Path(lot_de_plateaux_parent_1.chemin_enregistrement).exists() \
            and not Path(lot_de_plateaux_parent_2.chemin_enregistrement).exists():
            logger.info(f"Copie parent 1 uniquement {lot_de_plateaux_parent_1.chemin_enregistrement}")
            self.copier_parent(lot_de_plateaux_parent_1.chemin_enregistrement,
                                nb_colonnes, nb_lignes, reset_filtre=False)
            return
        if not Path(lot_de_plateaux_parent_1.chemin_enregistrement).exists() \
            and Path(lot_de_plateaux_parent_2.chemin_enregistrement).exists():
            logger.info(f"Copie parent 2 uniquement {lot_de_plateaux_parent_2.chemin_enregistrement}")
            self.copier_parent(lot_de_plateaux_parent_2.chemin_enregistrement,
                                nb_colonnes, nb_lignes, reset_filtre=False)
            return

        if lot_de_plateaux_parent_1.est_filtre_doublons_permutation_piles \
            and lot_de_plateaux_parent_2.est_filtre_doublons_permutation_piles:
            # Copie des fichiers
            if self._repertoire_analyse_1 != self._repertoire_filtre:
                self._chrono.start()
                self.copier_parent(lot_de_plateaux_parent_1.chemin_enregistrement,
                                   nb_colonnes, nb_lignes)
                self._chrono.pause()
            lot_de_plateaux_parent_1 = None

            lot_de_plateaux = LotDePlateaux((nb_colonnes, nb_lignes, self._nb_colonnes_vides),
                                            repertoire_export_json=self._repertoire_filtre,
                                            nb_plateaux_max = self._memoire_max)
            if not lot_de_plateaux.est_filtre_doublons_permutation_jetons_piles:
                logger.info(f"Début de fusion et filtrage des 2 parents")
                # Fusionner le parent 2 et le liberer
                self._chrono.start()
                plateaux_valides_parent_2 = lot_de_plateaux_parent_2.plateaux_valides
                plateaux_valides_filtre = lot_de_plateaux.plateaux_valides
                lot_de_plateaux._ensemble_des_plateaux_valides.update(plateaux_valides_parent_2)
                plateaux_valides_parent_2.clear()
                lot_de_plateaux_parent_2 = None
                self._chrono.pause()

                # Parcourir les plateaux et supprimer les plateaux "invalides"
                self._chrono.start()
                lot_de_plateaux.filtrer_doublons_permutation_jetons_piles(self._periode_affichage)
                self._chrono.pause()
                logger.info(f"Fusion et filtrage des 2 parents achevé")
                logger.info(f"Traitement {self._nom_etape} en {self._chrono} secondes")
            else:
                logger.info(f"Le filtrage est deja acheve.")
            self._done = True
        else:
            self._done = False
            logger.info(f"Le filtrage parent n'est pas acheve.")
        # logger.info(f"FIN {self._nom_etape}")

    def chercher_en_boucle(self):
        logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")
        while(True):
            # logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
            # Parcourir aléatoirement pour pouvoir lancer plusieurs scripts en parallele san conflit de fichiers.
            liste_colonne_ligne = [{'colonnes':c, 'lignes':l} for c in self._nb_colonnes for l in self._nb_lignes]
            random.shuffle(liste_colonne_ligne)
            for colonne_ligne in liste_colonne_ligne:
                self.filtrer_les_plateaux(colonne_ligne.get('colonnes'), colonne_ligne.get('lignes'))
            # logger.info('-'*10 + " FIN " + '-'*10)
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            logger.info(f"{current_time} - Attente entre 2 iterations de {self._periode_scrutation_secondes}s...")
            time.sleep(self._periode_scrutation_secondes)

    def chercher_en_sequence(self):
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        # logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        # Parcourir aléatoirement pour pouvoir lancer plusieurs scripts en parallele san conflit de fichiers.
        liste_colonne_ligne = [{'colonnes':c, 'lignes':l} for c in self._nb_colonnes for l in self._nb_lignes]
        random.shuffle(liste_colonne_ligne)
        for colonne_ligne in liste_colonne_ligne:
            self.filtrer_les_plateaux(colonne_ligne.get('colonnes'), colonne_ligne.get('lignes'))
        # logger.info('-'*10 + " FIN " + '-'*10)

    def chercher_en_parallele(self):
        profil = ProfilerLeCode(self._nom_tache, self._profiler_le_code)
        profil.start()

        taches = CreerLesTaches(nom=self._nom_tache, liste_colonnes=self._nb_colonnes, liste_lignes=self._nb_lignes)
        
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_parallele.NOUVELLE-RECHERCHE")
        # logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)

        # taches.exporter()
        taches.importer()
        taches.executer_taches(self.filtrer_les_plateaux)
        # logger.info('-'*10 + " FIN " + '-'*10)

        profil.stop()

if __name__ == "__main__":
    NOM_TACHE = 'fusionner_filtrer_doublons_permutation_jetons_piles'
    FICHIER_JOURNAL = Path('..') / 'logs' / f'{NOM_TACHE}.log'
    REPERTOIRE_ANALYSE_1 = Path('..') / '..' / 'Pipelines' / 'pipeline_5_filtre_doublons_permutation_jetons_piles'
    REPERTOIRE_ANALYSE_2 = Path('..') / '..' / 'Pipelines_rapide' / 'pipeline_5_filtre_doublons_permutation_jetons_piles'
    REPERTOIRE_FILTRE = Path('..') / '..' / 'Pipelines' / 'pipeline_6_fusion_filtre_doublons_permutation_jetons_piles'

    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    filtrer = FusionnerFiltrerLesPlateaux(
        nb_colonnes=[3], #range(3, 12),
        nb_lignes=[3], #range(3,14),
        nb_colonnes_vides=1,
        repertoire_analyse_1=str(REPERTOIRE_ANALYSE_1),
        repertoire_analyse_2=str(REPERTOIRE_ANALYSE_2),
        repertoire_filtre=str(REPERTOIRE_FILTRE),
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL,
        periode_scrutation_secondes = 1 * 60 * 60 # 1h
    )
    # filtrer.chercher_en_parallele()
    filtrer.chercher_en_sequence()
    # filtrer.chercher_en_boucle()
