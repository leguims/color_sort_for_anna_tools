"Parcourt les plateaux et pratique un elagage des doublons et de similarite"
import logging
import pathlib

from lot_de_plateaux import LotDePlateaux
from profiler_le_code import ProfilerLeCode
from creer_les_taches import CreerLesTaches

COLONNES = [3] #range(2, 12) #[2] # range(2, 5) # range(2, 5) #11
LIGNES = [6] #range(2,6) #[5] #range(2,6) #range(2, 14) #[3] # [2,3] #4
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 5_000_000
PROFILER_LE_CODE = False
NOM_TACHE = 'revalider_les_plateaux'
FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'
PERIODE_AFFICHAGE = 1*60 # en secondes
REPERTOIRE_ANALYSE = 'Analyse_nouvelle_architecture'

def revalider_les_plateaux(colonnes, lignes):
    # Configurer le logger en doublon pour la paralelisation
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"{colonnes}.{lignes}.{NOM_TACHE}")
    logger.info(f"DEBUT")
    lot_de_plateaux = LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX),
                                    repertoire_export_json=REPERTOIRE_ANALYSE,
                                    nb_plateaux_max = MEMOIRE_MAX)
    # Parcourir les plateaux et supprimer les plateaux "invalides"
    lot_de_plateaux.mettre_a_jour_les_plateaux_valides(PERIODE_AFFICHAGE)

def chercher_en_sequence(colonnes=COLONNES, lignes=LIGNES):
    # Configurer le logger
    logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
    for iter_lignes in lignes:
        for iter_colonnes in colonnes:
            revalider_les_plateaux(iter_colonnes, iter_lignes)
    logger.info('-'*10 + " FIN " + '-'*10)

def chercher_en_parallele(colonnes=COLONNES, lignes=LIGNES):
    profil = ProfilerLeCode(NOM_TACHE, PROFILER_LE_CODE)
    profil.start()

    taches = CreerLesTaches(nom=NOM_TACHE, liste_colonnes=colonnes, liste_lignes=lignes)
    
    # Configurer le logger
    logger = logging.getLogger(f"chercher_en_parallele.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)

    # taches.exporter()
    taches.importer()
    taches.executer_taches(revalider_les_plateaux)
    logger.info('-'*10 + " FIN " + '-'*10)

    profil.stop()

if __name__ == "__main__":
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # chercher_en_parallele()
    chercher_en_sequence()
