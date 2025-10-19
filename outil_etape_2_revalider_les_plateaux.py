"Parcourt les plateaux et pratique un elagage des doublons et de similarite"
import logging
import pathlib

from lot_de_plateaux import LotDePlateaux
from profiler_le_code import ProfilerLeCode
from creer_les_taches import CreerLesTaches

class RevaliderLesPlateaux:
    "Parcourt les plateaux et pratique un elagage des doublons et de similarite"
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                repertoire_analyse,
                nom_tache,
                fichier_journal,
                memoire_max = 5_000_000,
                profiler_le_code = False,
                periode_affichage = 1*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse = repertoire_analyse
        self._nom_tache = nom_tache
        self._fichier_journal = fichier_journal
        self._memoire_max = memoire_max
        self._profiler_le_code = profiler_le_code
        self._periode_affichage = periode_affichage

    def revalider_les_plateaux(self, nb_colonnes, nb_lignes):
        # Configurer le logger en doublon pour la paralelisation
        logging.basicConfig(filename=self._fichier_journal, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{nb_colonnes}.{nb_lignes}.{self._nom_tache}")
        logger.info(f"DEBUT")
        lot_de_plateaux = LotDePlateaux((nb_colonnes, nb_lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse,
                                        nb_plateaux_max = self._memoire_max)
        # Parcourir les plateaux et supprimer les plateaux "invalides"
        lot_de_plateaux.mettre_a_jour_les_plateaux_valides(self._periode_affichage)

    def chercher_en_sequence(self):
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for iter_lignes in self._nb_lignes:
            for iter_colonnes in self._nb_colonnes:
                self.revalider_les_plateaux(iter_colonnes, iter_lignes)
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
        taches.executer_taches(self.revalider_les_plateaux)
        logger.info('-'*10 + " FIN " + '-'*10)

        profil.stop()

if __name__ == "__main__":
    NOM_TACHE = 'revalider_les_plateaux'
    FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    revalider = RevaliderLesPlateaux(
        nb_colonnes=[3], #range(2, 12) #[2] # range(2, 5) # range(2, 5) #11
        nb_lignes=[4], #range(2,6) #[5] #range(2,6) #range(2, 14) #[3] # [2,3] #4
        nb_colonnes_vides=1,
        repertoire_analyse='Analyse_nouvelle_architecture',
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL
    )
    # revalider.chercher_en_parallele()
    revalider.chercher_en_sequence()
