"Module pour convertir tous les JSON existants en 'texte_universel'"
import logging
import pathlib

import color_wood_sort as cws

COLONNES = range(2, 12) #[2] # range(2, 5) # range(2, 5) #11
LIGNES = range(2, 14) #[3] # [2,3] #4
COLONNES_VIDES_MAX = 1
PROFILER_LE_CODE = False
NOM_TACHE = 'conversion_des_plateaux_en_texte_universel'
FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

def conversion_des_plateaux_en_texte_universel(colonnes, lignes):
    # Configurer le logger
    logger = logging.getLogger(f"{colonnes}.{lignes}.{NOM_TACHE}")
    logger.info(f"DEBUT")
    lot_de_plateaux = cws.LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX))
    lot_de_plateaux.est_deja_termine()

    # Forcer la réécriture du JSON pour mettre à jour le format universel
    lot_de_plateaux._a_change = True
    lot_de_plateaux.exporter_fichier_json()

def chercher_en_sequence():
    # Configurer le logger
    logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
    for lignes in LIGNES:
        for colonnes in COLONNES:
            conversion_des_plateaux_en_texte_universel(colonnes, lignes)
    logger.info('-'*10 + " FIN " + '-'*10)

def chercher_en_parallele():
    profil = cws.ProfilerLeCode(NOM_TACHE, PROFILER_LE_CODE)
    profil.start()

    taches = cws.CreerLesTaches(nom=NOM_TACHE, liste_colonnes=COLONNES, liste_lignes=LIGNES)

    # Configurer le logger
    logger = logging.getLogger(f"chercher_en_parallele.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)

    # taches.exporter()
    taches.importer()
    taches.executer_taches(conversion_des_plateaux_en_texte_universel)
    logger.info('-'*10 + " FIN " + '-'*10)

    profil.stop()

if __name__ == "__main__":
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #chercher_en_parallele()
    chercher_en_sequence()