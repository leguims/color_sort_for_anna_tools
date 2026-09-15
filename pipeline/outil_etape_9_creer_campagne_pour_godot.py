"""Crée un fichier directement intégrable dans la production GODOT.
- Crée la campagne
- Crée chaque niveau par difficulté et nombre de plateaux
- Vérifie que les plateaux sont inédits (dans aucune autre campagne)"""
import logging
from pathlib import Path
import random

import sys
import os
# pour importer depuis le dossier parent
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from io_utils.export_json import ExportJSON
from io_utils.chrono import Chrono

class CreerLaCampagnePourGodot:
    """Parcourt 'Solutions_classees.json' et crée un fichier de campagne pour Godot"""
    def __init__(self,
                repertoire_solution,
                fichier_solution,
                fichier_campagne,
                fichier_configuration_campagne,
                nom_etape,
                fichier_journal):
        self._repertoire_solution = repertoire_solution
        self._fichier_solution = fichier_solution
        self._fichier_campagne = fichier_campagne
        self._fichier_configuration_campagne = fichier_configuration_campagne
        self._nom_etape = nom_etape
        self._fichier_journal = fichier_journal
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._chrono = Chrono()

    @property
    def elapsed(self):
        return self._chrono.elapsed

    def exporter_campagne_pour_godot(self):
        # Configurer le logger
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{self._nom_etape}")
        logger.info(f"DEBUT {self._nom_etape}")

        solutions_godot_json = ExportJSON(
            delai=60, longueur=100, nom_plateau='',
            nom_export=self._fichier_solution,
            repertoire=self._repertoire_solution)
        solutions_godot = solutions_godot_json.importer()
        liste_difficulte_godot = solutions_godot.get('liste difficulte des plateaux', {})

        current_dir = os.path.dirname(os.path.abspath(__file__))
        configuration_campagne_godot_json = ExportJSON(
                delai=60, longueur=100, nom_plateau='',
                nom_export=self._fichier_configuration_campagne,
                repertoire=current_dir)
        configuration_campagne = configuration_campagne_godot_json.importer()

        self._chrono.start()
        # Creation du fichier de campagne pour Godot
        campagne_godot = {
            "nom": configuration_campagne.get("nom", ""),
            "description": configuration_campagne.get("description", ""),
            "nb_niveaux": configuration_campagne.get("nb_niveaux", ""),
            "nb_plateaux": configuration_campagne.get("nb_plateaux", 100),
            "niveaux": []
            }
        # Construire les niveaux 1 par un
        # Vérifier les doublons
        plateaux_vus = set()
        # Vérifier les absences
        liste_echec_recherche = []
        for conf_niveau in configuration_campagne.get("niveaux", []):
            niveau_godot = {
                "nom": conf_niveau.get("nom", ""),
                "nb_plateaux": conf_niveau.get("nb_plateaux", ""),
                "plateaux": []
            }
            # Selectionner les plateaux pour ce niveau
            plateaux_godot = []
            plateaux_doublons = []
            for conf_plateau in conf_niveau.get("plateaux", []):
                difficulte_min = conf_plateau.get("difficulte", {}).get("min", 1)
                difficulte_max = conf_plateau.get("difficulte", {}).get("max", 99)
                gameplay = conf_plateau.get("gameplay", "CLASSIQUE")
                logger.info(f"{self._nom_etape} Recherche : difficulte [{difficulte_min}-{difficulte_max}], gameplay {gameplay}")
                # Parcourir les solutions pour trouver l'élu (choix de difficulté aleatoire)
                plateau_godot = None
                cpt_iteration = 1
                while not plateau_godot:
                    logger.info(f"{self._nom_etape} While not plateau_godot... {cpt_iteration}")
                    for difficulte in random.sample(range(difficulte_min, difficulte_max + 1),
                                        k=difficulte_max-difficulte_min+1):
                        difficulte_str = str(difficulte).zfill(3)
                        if difficulte_str in liste_difficulte_godot:
                            # Selectionner un plateau aleatoire
                            plateau_godot = random.choice(solutions_godot['liste difficulte des plateaux'][difficulte_str])
                            if plateau_godot.get("gameplay") == gameplay:
                                plateaux_godot.append(plateau_godot)
                                logger.info(f"{self._nom_etape} Trouve : difficulte= {plateau_godot.get('difficulte')}, gameplay {plateau_godot.get('gameplay')}")
                                # Verifier les doublons
                                plateau_tuple = (plateau_godot.get("nom"), plateau_godot.get("gameplay"))
                                if plateau_tuple in plateaux_vus:
                                    plateaux_doublons.append(plateau_godot)
                                else:
                                    plateaux_vus.add(plateau_tuple)
                                # Sortir de l'itération "difficulté"
                                break
                            # Tenter une autre difficulté
                            plateau_godot = None
                            continue
                    if not plateau_godot:
                        cpt_iteration += 1
                        if cpt_iteration >= 100:
                            liste_echec_recherche.append(conf_plateau)
                            break    # Sortie du while.
                            # raise ValueError(f"Aucun plateau trouvé pour la configuration : {conf_plateau}")
            niveau_godot["plateaux"] = plateaux_godot
            campagne_godot["niveaux"].append(niveau_godot)
            if plateaux_doublons:
                logger.error(f"Doublons trouves dans le niveau '{niveau_godot.get('nom', 'inconnu')}': {plateaux_doublons}")
        self._chrono.pause()
        logger.info(f"Traitement {self._nom_etape} en {self._chrono} secondes")
        export_godot_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                       nom_export=self._fichier_campagne+'_'+campagne_godot["nom"].replace(" ", "_"),
                                       repertoire=self._repertoire_solution)
        export_godot_json.effacer()
        export_godot_json.forcer_export(campagne_godot)

        if liste_echec_recherche:
            logger.error(f"Configurations de plateau non trouvees : {liste_echec_recherche}")
        logger.info("Export termine")


if __name__ == "__main__":
    NOM_ETAPE = 'creer_campagne_pour_godot'
    FICHIER_JOURNAL = Path('..') / 'logs' / f'{NOM_ETAPE}.log'
    FICHIER_SOLUTION = Path('..') / '..' / 'Pipelines' / 'pipeline_6_solutions'
    # FICHIER_JOURNAL = Path('logs') / f'{NOM_ETAPE}.log' # DEBUG
    # FICHIER_SOLUTION = Path('Pipelines') / 'pipeline_6_solutions' # DEBUG

    # Configurer le logger
    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    solutions_godot = CreerLaCampagnePourGodot(
        repertoire_solution=str(FICHIER_SOLUTION),
        fichier_solution='8_solutions_godot',
        fichier_campagne='9_campagne_godot',
        fichier_configuration_campagne='outil_etape_9_structure_campagne_godot',
        nom_etape=NOM_ETAPE,
        fichier_journal=FICHIER_JOURNAL,
    )
    solutions_godot.exporter_campagne_pour_godot()
