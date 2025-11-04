"Module pour convertir tous les JSON de solutions existants dans le nouveau format sans réaliser la rechercher"
import logging
import pathlib

from export_json import ExportJSON

COLONNES = range(2, 12)
LIGNES = range(2, 14)
NOM_TACHE = 'conversion_des_anciennes_solutions'
FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'
REPERTOIRE_SOLUTIONS_ANCIEN_FORMAT = pathlib.Path('Solutions')
REPERTOIRE_SOLUTIONS_NOUVEAU_FORMAT = pathlib.Path('Solutions_nouveau_format')

def conversion_des_anciennes_solutions(colonnes, lignes):
    # Configurer le logger
    logger = logging.getLogger(f"{colonnes}.{lignes}.{NOM_TACHE}")
    logger.info(f"DEBUT")

    # Parcourir les fichiers correspondant au motif '*_Resolution_*.json'
    nom_plateau = f"Plateaux_{colonnes}x{lignes}"
    REPERTOIRE_SOLUTIONS_PLATEAUX = REPERTOIRE_SOLUTIONS_ANCIEN_FORMAT / nom_plateau
    if REPERTOIRE_SOLUTIONS_ANCIEN_FORMAT.exists() \
        and REPERTOIRE_SOLUTIONS_PLATEAUX.exists():
        fichiers = REPERTOIRE_SOLUTIONS_PLATEAUX.glob("*_Resolution_*.json")
        # Creer les nouveaux repertoire
        REPERTOIRE_SOLUTIONS_NOUVEAU_FORMAT_PLATEAUX = REPERTOIRE_SOLUTIONS_NOUVEAU_FORMAT / nom_plateau
        REPERTOIRE_SOLUTIONS_NOUVEAU_FORMAT_PLATEAUX.mkdir(parents=True, exist_ok=True)

        # Traiter chaque solution
        for fichier in fichiers:
            logger.info(fichier.stem)
            # Ouvrir ancienne solution et nouveau
            export_json_solution_ancienne = ExportJSON(delai=60, longueur=100,
                                    nom_plateau=nom_plateau,
                                    nom_export=fichier.stem,
                                    repertoire = str(REPERTOIRE_SOLUTIONS_ANCIEN_FORMAT))
            export_json_solution_nouvelle = ExportJSON(delai=60, longueur=100,
                                    nom_plateau=nom_plateau,
                                    nom_export=fichier.stem,
                                    repertoire = str(REPERTOIRE_SOLUTIONS_NOUVEAU_FORMAT))

            # Lire le contenu
            ancien_json = export_json_solution_ancienne.importer()
            nouveau_json = export_json_solution_nouvelle.importer()
            # Vérifier que le nouveau fichier n'est pas deja converti
            if 'recherche terminee' not in nouveau_json:
                # Convertir au nouveau format
                nouveau_json = {}
                if 'plateau' in ancien_json:
                    nouveau_json['plateau'] = ancien_json.get('plateau')
                if 'liste des solutions' in ancien_json:
                    nouveau_json["dico des longueurs"] = {}
                    nouveau_json["solution"] = []
                    for solution in ancien_json.get('liste des solutions'):
                        if len(solution) not in nouveau_json.get("dico des longueurs"):
                            nouveau_json["dico des longueurs"][len(solution)] = 1
                        else:
                            nouveau_json["dico des longueurs"][len(solution)] += 1
                        if not nouveau_json["solution"] \
                            or len(solution) < len(nouveau_json["solution"]):
                            nouveau_json["solution"] = solution
                nouveau_json['recherche terminee'] = True
    
                # Enregistrer le nouveau format
                export_json_solution_nouvelle.forcer_export(nouveau_json)

def chercher_en_sequence():
    # Configurer le logger
    logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
    logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
    for lignes in LIGNES:
        for colonnes in COLONNES:
            conversion_des_anciennes_solutions(colonnes, lignes)
    logger.info('-'*10 + " FIN " + '-'*10)

if __name__ == "__main__":
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    chercher_en_sequence()
