"Module pour créer des plateaux de 'ColorWoodSort'"
import color_wood_sort as cws
import logging
import pathlib

COLONNES = range(2, 12) #[2] # range(2, 5) # range(2, 5) #11
LIGNES = range(2, 14) #[3] # [2,3] #4
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 5_000_000
PROFILER_LE_CODE = False
NOM_TACHE = 'revalider_les_plateaux'
FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

def revalider_les_plateaux(colonnes, lignes):
    # Configurer le logger
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"{colonnes}.{lignes}.{NOM_TACHE}")
    logger.info(f"{' '*colonnes} DEBUT")
    lot_de_plateaux = cws.LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX), nb_plateaux_max = MEMOIRE_MAX)
    lot_de_plateaux.est_deja_termine()
    # Parcourir les plateaux et supprimer les plateaux "invalides"
    lot_de_plateaux.mettre_a_jour_les_plateaux_valides()

def chercher_en_sequence():
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
    for lignes in LIGNES:
        for colonnes in COLONNES:
            revalider_les_plateaux(colonnes, lignes)
    logger.info('-'*10 + " FIN " + '-'*10)

def chercher_en_parallele():
    profil = cws.ProfilerLeCode(NOM_TACHE, PROFILER_LE_CODE)
    profil.start()

    taches = cws.CreerLesTaches(nom=NOM_TACHE, nb_colonnes=max(COLONNES)+1, nb_lignes=max(LIGNES)+1)
    
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(f"chercher_en_parallele.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)

    # taches.exporter()
    taches.importer()
    taches.executer_taches(revalider_les_plateaux)
    logger.info('-'*10 + " FIN " + '-'*10)

    profil.stop()

if __name__ == "__main__":
    chercher_en_parallele()
    # chercher_en_sequence()