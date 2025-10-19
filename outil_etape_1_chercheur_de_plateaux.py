"Module pour creer des plateaux de 'ColorWoodSort'"
import logging
import pathlib
import datetime

from lot_de_plateaux import LotDePlateaux
from profiler_le_code import ProfilerLeCode
from creer_les_taches import CreerLesTaches

class ChercherDesPlateaux:
    "Module pour creer des plateaux de 'ColorWoodSort'"
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                repertoire_analyse,
                nom_tache,
                fichier_journal,
                profiler_le_code = False,
                periode_affichage = 1*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse = repertoire_analyse
        self._nom_tache = nom_tache
        self._fichier_journal = fichier_journal
        self._profiler_le_code = profiler_le_code
        self._periode_affichage = periode_affichage

    def chercher_des_plateaux(self, colonnes, lignes):
        # Configurer le logger en doublon pour la paralelisation
        logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{colonnes}.{lignes}.{NOM_TACHE}")
        logger.info(f"DEBUT")
        lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse)
        if not lot_de_plateaux.est_deja_termine():
            dernier_affichage  = datetime.datetime.now().timestamp()
            for plateau_ligne_texte_universel in lot_de_plateaux:
                if datetime.datetime.now().timestamp() - dernier_affichage > self._periode_affichage:
                    logger.info(f"plateau_ligne_texte_universel = '{plateau_ligne_texte_universel}'")
                    dernier_affichage  = datetime.datetime.now().timestamp()
                pass
            logger.info(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
            logger.info(f"nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
        else:
            logger.info(f"Ce lot de plateaux est deja termine")


    def chercher_en_sequence(self):
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for iter_lignes in self._nb_lignes:
            for iter_colonnes in self._nb_colonnes:
                self.chercher_des_plateaux(iter_colonnes, iter_lignes)
        logger.info('-'*10 + " FIN " + '-'*10)

    def chercher_en_parallele(self):
        profil = ProfilerLeCode(NOM_TACHE, self._profiler_le_code)
        profil.start()

        taches = CreerLesTaches(nom=NOM_TACHE, liste_colonnes=self._nb_colonnes, liste_lignes=self._nb_lignes)

        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_parallele.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)

        # taches.exporter()
        taches.importer()
        taches.executer_taches(self.chercher_des_plateaux)
        logger.info('-'*10 + " FIN " + '-'*10)

        profil.stop()

if __name__ == "__main__":
    NOM_TACHE = 'chercher_des_plateaux'
    FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    chercher_plateaux = ChercherDesPlateaux(
        nb_colonnes=[3], #range(2, 12) #[2] # range(2, 5) # range(2, 5) #11
        nb_lignes=[4], #range(2,6) #[5] #range(2,6) #range(2, 14) #[3] # [2,3] #4
        nb_colonnes_vides=1,
        repertoire_analyse='Analyse_nouvelle_architecture',
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL
    )
    # chercher_plateaux.chercher_en_parallele()
    chercher_plateaux.chercher_en_sequence()
