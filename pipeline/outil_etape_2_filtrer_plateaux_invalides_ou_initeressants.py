"Parcourt les plateaux et pratique un elagage des doublons et de similarite"
import logging
from pathlib import Path
import shutil

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # pour importer depuis le dossier parent

from core.lot_de_plateaux import LotDePlateaux
from io_utils.profiler_le_code import ProfilerLeCode
from io_utils.creer_les_taches import CreerLesTaches

class FiltrerLesPlateaux:
    "Parcourt les plateaux et pratique un elagage des doublons et de similarite"
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                repertoire_analyse,
                repertoire_filtre,
                nom_tache,
                fichier_journal,
                memoire_max = 5_000_000,
                profiler_le_code = False,
                periode_affichage = 1*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse = repertoire_analyse
        self._repertoire_filtre = repertoire_filtre
        self._nom_tache = nom_tache
        self._nom_etape = 'revalider_les_plateaux'
        self._fichier_journal = fichier_journal
        self._memoire_max = memoire_max
        self._profiler_le_code = profiler_le_code
        self._periode_affichage = periode_affichage

    def copier_les_plateaux(self, source: Path):
        # Copie le repertoire 'Plateaux_XX_YY' et le fichier JSON
        destination = Path(self._repertoire_filtre)
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source.parent.parent, destination, dirs_exist_ok=True) # Copier les fichiers d'analyse dans le repertoire de filtre pour les modifier

    def filtrer_les_plateaux(self, nb_colonnes, nb_lignes):
        # Configurer le logger en doublon pour la paralelisation
        logging.basicConfig(filename=self._fichier_journal, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{nb_colonnes}.{nb_lignes}.{self._nom_etape}")
        logger.info(f"DEBUT {self._nom_etape}")

        # Copie des fichiers
        if self._repertoire_analyse != self._repertoire_filtre:
            lot_de_plateaux = LotDePlateaux((nb_colonnes, nb_lignes, self._nb_colonnes_vides),
                                            repertoire_export_json=self._repertoire_analyse,
                                            nb_plateaux_max = self._memoire_max)
            self.copier_les_plateaux(lot_de_plateaux.chemin_enregistrement)

        lot_de_plateaux = LotDePlateaux((nb_colonnes, nb_lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_filtre,
                                        nb_plateaux_max = self._memoire_max)
        # Parcourir les plateaux et supprimer les plateaux "invalides"
        lot_de_plateaux.filtrer_plateaux_invalides_ou_initeressants(self._periode_affichage)

    def chercher_en_sequence(self):
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for iter_lignes in self._nb_lignes:
            for iter_colonnes in self._nb_colonnes:
                self.filtrer_les_plateaux(iter_colonnes, iter_lignes)
        logger.info('-'*10 + " FIN " + '-'*10)

    def chercher_en_parallele(self):
        profil = ProfilerLeCode(self._nom_tache, self._profiler_le_code)
        profil.start()

        taches = CreerLesTaches(nom=self._nom_tache, liste_colonnes=self._nb_colonnes, liste_lignes=self._nb_lignes)
        
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_parallele.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)

        # taches.exporter()
        taches.importer()
        taches.executer_taches(self.filtrer_les_plateaux)
        logger.info('-'*10 + " FIN " + '-'*10)

        profil.stop()

if __name__ == "__main__":
    NOM_TACHE = 'filtrer_plateaux_invalides_ou_initeressants'
    FICHIER_JOURNAL = Path('logs') / f'{NOM_TACHE}.log'

    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    revalider = FiltrerLesPlateaux(
        nb_colonnes=[3], #range(2, 12) #[2] # range(2, 5) # range(2, 5) #11
        nb_lignes=[3], #range(2,6) #[5] #range(2,6) #range(2, 14) #[3] # [2,3] #4
        nb_colonnes_vides=1,
        repertoire_analyse='pipeline_analyse', # 'Analyse_nouvelle_architecture',
        repertoire_filtre='pipeline_filtre_1', # 'Analyse_nouvelle_architecture_filtre_1',
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL
    )
    # revalider.chercher_en_parallele()
    revalider.chercher_en_sequence()
