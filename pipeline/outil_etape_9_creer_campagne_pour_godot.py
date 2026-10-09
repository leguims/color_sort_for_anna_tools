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
                fichier_solution_classique,
                fichier_solution_qui_perd_gagne,
                fichier_campagne,
                fichier_configuration_campagne,
                nom_etape,
                fichier_journal):
        self._repertoire_solution = repertoire_solution
        self._fichier_solution_classique = fichier_solution_classique
        self._fichier_solution_qui_perd_gagne = fichier_solution_qui_perd_gagne
        self._fichier_campagne = fichier_campagne
        self._fichier_configuration_campagne = fichier_configuration_campagne
        self._nom_etape = nom_etape
        self._fichier_journal = fichier_journal
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._chrono = Chrono()

        # Configurer le logger
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._logger = logging.getLogger(f"{self._nom_etape}")

    @property
    def elapsed(self):
        return self._chrono.elapsed

    def exporter_campagne_pour_godot(self):
        self._logger.info(f"DEBUT {self._nom_etape}")

        # Ouvrir tous les fichiers de solutions par GAMEPLAY
        # outil_etape_8_filtrer_les_solutions_CLASSIQUE_pour_godot.py
        solutions_CLASSIQUE_godot_json = ExportJSON(
            delai=60, longueur=100, nom_plateau='',
            nom_export=self._fichier_solution_classique,
            repertoire=self._repertoire_solution)
        solutions_CLASSIQUE_godot = solutions_CLASSIQUE_godot_json.importer()
        liste_difficulte_CLASSIQUE_godot = solutions_CLASSIQUE_godot.get('liste difficulte des plateaux', {})

        # outil_etape_8_filtrer_les_solutions_QUI_PERD_GAGNE_pour_godot.py
        solutions_QUI_PERD_GAGNE_godot_json = ExportJSON(
            delai=60, longueur=100, nom_plateau='',
            nom_export=self._fichier_solution_qui_perd_gagne,
            repertoire=self._repertoire_solution)
        solutions_QUI_PERD_GAGNE_godot = solutions_QUI_PERD_GAGNE_godot_json.importer()
        liste_difficulte_QUI_PERD_GAGNE_godot = solutions_QUI_PERD_GAGNE_godot.get('liste difficulte des plateaux', {})


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
            solutions_godot = {}
            liste_difficulte_godot = {}
            for conf_plateau in conf_niveau.get("plateaux", []):
                difficulte_min = conf_plateau.get("difficulte", {}).get("min", 1)
                difficulte_max = conf_plateau.get("difficulte", {}).get("max", 99)

                # Selon le gameplay, consulter le bon fichiers de solutions
                gameplay = conf_plateau.get("gameplay", "CLASSIQUE")
                if gameplay == "CLASSIQUE":
                    solutions_godot = solutions_CLASSIQUE_godot
                    liste_difficulte_godot = liste_difficulte_CLASSIQUE_godot
                elif gameplay == "QUI_PERD_GAGNE":
                    solutions_godot = solutions_QUI_PERD_GAGNE_godot
                    liste_difficulte_godot = liste_difficulte_QUI_PERD_GAGNE_godot
                else:
                    raise ValueError(f"Gameplay inconnu : {gameplay}")

                self._logger.info(f"{self._nom_etape} Recherche : difficulte [{difficulte_min}-{difficulte_max}], gameplay {gameplay}")
                # Parcourir les solutions pour trouver l'élu (choix de difficulté aleatoire)
                plateau_godot = None
                cpt_iteration = 1
                while not plateau_godot:
                    self._logger.info(f"{self._nom_etape} While not plateau_godot... {cpt_iteration}")
                    for difficulte in random.sample(range(difficulte_min, difficulte_max + 1),
                                        k=difficulte_max-difficulte_min+1):
                        difficulte_str = str(difficulte).zfill(3)
                        self._logger.info(f"{self._nom_etape}    Recherche : difficulte {difficulte_str}")
                        if difficulte_str in liste_difficulte_godot:
                            # Selectionner un plateau aleatoire
                            plateau_godot = random.choice(solutions_godot['liste difficulte des plateaux'][difficulte_str])
                            self._logger.info(f"{self._nom_etape}    Recherche : plateau {plateau_godot}")
                            # Verifier les doublons
                            plateau_tuple = (plateau_godot.get("nom"), plateau_godot.get("gameplay"))
                            if plateau_tuple in plateaux_vus:
                                plateaux_doublons.append(plateau_godot)
                                # Poursuivre la recherche
                                self._logger.info(f"{self._nom_etape}    Recherche : plateau en doublon {plateau_godot.get('nom')}")
                            else:
                                # Le plateau est nouveau. Youpi !
                                plateaux_godot.append(plateau_godot)
                                self._logger.info(f"{self._nom_etape}    Trouve : difficulte= {plateau_godot.get('difficulte')}, gameplay {plateau_godot.get('gameplay')}")
                                plateaux_vus.add(plateau_tuple)
                                # Sortir de l'itération "difficulté"
                                break
                        else:
                            self._logger.info(f"{self._nom_etape}    Recherche : difficulte {difficulte_str} absente")
                        # Tenter une autre difficulté
                        plateau_godot = None
                    if not plateau_godot:
                        cpt_iteration += 1
                        if cpt_iteration >= 100:
                            liste_echec_recherche.append(conf_plateau)
                            break    # Sortie du while.
                            # raise ValueError(f"Aucun plateau trouvé pour la configuration : {conf_plateau}")
            niveau_godot["plateaux"] = plateaux_godot
            campagne_godot["niveaux"].append(niveau_godot)
            if plateaux_doublons:
                self._logger.error(f"Doublons trouves dans le niveau '{niveau_godot.get('nom', 'inconnu')}': {plateaux_doublons}")
        self._chrono.pause()
        self._logger.info(f"Traitement {self._nom_etape} en {self._chrono} secondes")
        export_godot_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                       nom_export=self._fichier_campagne+'_'+campagne_godot["nom"].replace(" ", "_"),
                                       repertoire=self._repertoire_solution)
        export_godot_json.effacer()
        export_godot_json.forcer_export(campagne_godot)

        if liste_echec_recherche:
            self._logger.error(f"Configurations de plateau non trouvees : {liste_echec_recherche}")
        self._logger.info("Export termine")

    def auditer_campagne_pour_godot(self):
        # Configurer le logger
        self._logger.info(f"DEBUT {self._nom_etape} : audit de campagne")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        configuration_campagne_godot_json = ExportJSON(
                delai=60, longueur=100, nom_plateau='',
                nom_export=self._fichier_configuration_campagne,
                repertoire=current_dir)
        configuration_campagne = configuration_campagne_godot_json.importer()

        self._chrono.start()
        # Lecture du fichier de campagne pour Godot
        campagne_godot_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                       nom_export=self._fichier_campagne+'_'+configuration_campagne.get("nom", "").replace(" ", "_"),
                                       repertoire=self._repertoire_solution)
        campagne_godot = campagne_godot_json.importer()

        # Vérifier pour chaque niveau, l'écart avec la consigne
        audit_campagne = dict()
        audit_campagne['nom'] = configuration_campagne.get("nom", 'inconnu')
        for conf_niveau in configuration_campagne.get("niveaux", []):
            nom_niveau = conf_niveau.get("nom", "")
            nb_plateaux = conf_niveau.get("nb_plateaux", 0)
            indice_plateau = -1
            for conf_plateau in conf_niveau.get("plateaux", []):
                indice_plateau += 1
                difficulte_min = conf_plateau.get("difficulte", {}).get("min", 1)
                difficulte_max = conf_plateau.get("difficulte", {}).get("max", 99)
                gameplay = conf_plateau.get("gameplay", "CLASSIQUE")
                # self._logger.debug(f"{self._nom_etape} Verifier : difficulte [{difficulte_min}-{difficulte_max}], gameplay {gameplay}")

                # Vérifier le plateau dans la campagne Godot
                for campagne_niveau in campagne_godot.get("niveaux", []):
                    campagne_nom_niveau = campagne_niveau.get("nom", "")
                    if campagne_nom_niveau == nom_niveau:
                        campagne_liste_plateaux = campagne_niveau.get("plateaux", [])
                        if indice_plateau == 0:
                            # Verifier une seule fois par niveau
                            campagne_nb_plateaux = campagne_niveau.get("nb_plateaux", 0)
                            # Vérifier la taille, car cela compte !
                            if campagne_nb_plateaux != nb_plateaux:
                                self._logger.error(f"{self._nom_etape} '{nom_niveau}' Ecart 'nb_plateaux' : {indice_plateau+1} (attendu {nb_plateaux})")
                                if nom_niveau not in audit_campagne:
                                    audit_campagne[nom_niveau] = {}
                                audit_campagne[nom_niveau]['nb_plateaux'] = f"attendu {nb_plateaux}, trouve {campagne_nb_plateaux}"
                            elif campagne_nb_plateaux != len(campagne_liste_plateaux):
                                self._logger.error(f"{self._nom_etape} '{nom_niveau}' Plateaux absents : {campagne_nb_plateaux - len(campagne_liste_plateaux)}")
                                if nom_niveau not in audit_campagne:
                                    audit_campagne[nom_niveau] = {}
                                audit_campagne[nom_niveau]['nb_plateaux'] = f"Plateaux absents : {campagne_nb_plateaux - len(campagne_liste_plateaux)}"
                        elif indice_plateau < len(campagne_liste_plateaux):
                            plateau = campagne_liste_plateaux[indice_plateau]
                            # Vérifier la difficulté et le gameplay
                            campagne_gameplay = plateau.get("gameplay", "INCONNU")
                            if campagne_gameplay != gameplay:
                                self._logger.error(f"{self._nom_etape} '{nom_niveau}-Plateau {indice_plateau}' Ecart 'gameplay' : {campagne_gameplay} (attendu {gameplay})")
                                if nom_niveau not in audit_campagne:
                                    audit_campagne[nom_niveau] = {}
                                if indice_plateau not in audit_campagne[nom_niveau]:
                                    audit_campagne[nom_niveau][indice_plateau] = {}
                                audit_campagne[nom_niveau][indice_plateau]['gameplay'] = f"{campagne_gameplay} (attendu {gameplay})"

                            campagne_difficulte = int(plateau.get("difficulte", 0))
                            if campagne_difficulte < difficulte_min or campagne_difficulte > difficulte_max:
                                self._logger.error(f"{self._nom_etape} '{nom_niveau}-Plateau {indice_plateau}' Ecart 'difficulte': [{campagne_difficulte}] (attendu [{difficulte_min}-{difficulte_max}])")
                                if nom_niveau not in audit_campagne:
                                    audit_campagne[nom_niveau] = {}
                                if indice_plateau not in audit_campagne[nom_niveau]:
                                    audit_campagne[nom_niveau][indice_plateau] = {}
                                audit_campagne[nom_niveau][indice_plateau]['difficulte'] = f"{campagne_difficulte} (attendu [{difficulte_min}-{difficulte_max}])"
        self._chrono.pause()
        self._logger.info(f"Traitement {self._nom_etape} en {self._chrono} secondes")
        export_godot_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                       nom_export=self._fichier_campagne+'_'+campagne_godot["nom"].replace(" ", "_")+'_audit',
                                       repertoire=self._repertoire_solution)
        export_godot_json.effacer()
        export_godot_json.forcer_export(audit_campagne)
        self._logger.info(f"FIN {self._nom_etape} : audit de campagne")


if __name__ == "__main__":
    NOM_ETAPE = 'creer_campagne_pour_godot'
    NOM_DEPOT = 'color_sort_for_anna_tools'
    if Path().parent.resolve().name == NOM_DEPOT:
        # DEBUG
        FICHIER_JOURNAL = Path('logs') / f'{NOM_ETAPE}.log'
        FICHIER_SOLUTION = Path('Pipelines') / 'pipeline_7_solutions'
    elif Path().parent.resolve().name == (Path(NOM_DEPOT) / 'sources' / 'pipeline').name:
        FICHIER_JOURNAL = Path('..') / '..' / 'logs' / f'{NOM_ETAPE}.log'
        FICHIER_SOLUTION = Path('..') / '..' / 'Pipelines' / 'pipeline_7_solutions'
    else:
        print("Impossible de déterminer le chemin des fichiers en mode debug ou release.")
        exit(1)

    # Configurer le logger
    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    solutions_godot = CreerLaCampagnePourGodot(
        repertoire_solution=str(FICHIER_SOLUTION),
        fichier_solution_classique='8_filtrer_les_solutions_CLASSIQUE_pour_godot',
        fichier_solution_qui_perd_gagne='8_filtrer_les_solutions_QUI_PERD_GAGNE_pour_godot',
        fichier_campagne='9_campagne_godot',
        fichier_configuration_campagne='outil_etape_9_structure_campagne_godot',
        nom_etape=NOM_ETAPE,
        fichier_journal=FICHIER_JOURNAL
    )
    solutions_godot.exporter_campagne_pour_godot()
    solutions_godot.auditer_campagne_pour_godot()
