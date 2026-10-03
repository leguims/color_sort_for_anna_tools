"""Parcourt les plateaux resolus et les rassemble par GAMEPLAY dans un fichier dédié.
Les plateaux sont dans une écriture universelle avec les attributs spécifiques liés au GAMEPLAY.
Entrée : 'pipeline_5_filtre_doublons_permutation_jetons_piles'
Entrée : 'pipeline_6_solutions_unitaires'
Sortie : '7_filtrer_les_solutions_QUI_PERD_GAGNE_pour_godot'"""

import logging
from pathlib import Path

import sys
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from core.plateau import Plateau
from core.lot_de_plateaux import LotDePlateaux
from core.resoudre_plateau import ResoudrePlateau
from io_utils.export_json import ExportJSON

from pipeline.outil_etape_8_filtrer_les_solutions_CLASSIQUE_pour_godot import FiltrerLesSolutionsClassique

class FiltrerLesSolutionsQuiPerdGagne(FiltrerLesSolutionsClassique):
    """Parcourt les plateaux resolus et les rassemble dans le fichier
    'Solutions_classees.json' par difficulte avec une ecriture universelle"""
    def classer_les_solutions(self, colonnes, lignes):
        # Configurer le logger
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(f"{colonnes}.{lignes}.{self._nom_tache}")
        logger.info(f"DEBUT {self._nom_tache}")
        # logger.info(plateau.plateau_ligne_texte_universel)
        plateau = Plateau(colonnes, lignes, self._nb_colonnes_vides)
        lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse)

        if lot_de_plateaux.est_deja_termine:
            logger.info("Ce lot de plateaux est termine")

            logger.info("Importer les solutions QUI PERD GAGNE")
            solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=self._fichier_solution, repertoire=self._repertoire_solution)
            solutions_classees = solutions_classees_json.importer()
            plateau = Plateau(colonnes, lignes, self._nb_colonnes_vides)

            if "liste difficulte des plateaux" not in solutions_classees:
                solutions_classees["liste difficulte des plateaux"] = {}
            dict_difficulte = solutions_classees["liste difficulte des plateaux"]

            # Vérifier si ce type de plateau est deja present dans le fichier
            # Le premier enregistrement est vérifié :
            #     - s'il est present => 'deja_fait=True;verifier_deja_fait=False' et arret de la recherche
            #     - s'il est absent => 'deja_fait=False;verifier_deja_fait=False' et poursuite de la recherche
            deja_fait = False
            verifier_deja_fait = True
            # Trace pour l'avancement de la tache
            logger.info(f"Nombre de plateau a parcourir : {lot_de_plateaux.nb_plateaux_valides}")
            nb_plateaux_traites = 0
            avancement_affichage = {pourcentage: False for pourcentage in range(10, 100, 5)}
            # Parcourir chaque solution et remplir la structure de données
            for plateau_ligne_texte_a_filtrer in lot_de_plateaux.plateaux_valides:
                avancement = round(100. * nb_plateaux_traites / lot_de_plateaux.nb_plateaux_valides)
                if avancement in avancement_affichage and not avancement_affichage.get(avancement, True):
                    avancement_affichage[avancement] = True
                    logger.info(f"Avancement : {avancement}%")
                plateau.clear()
                plateau.plateau_ligne_texte = plateau_ligne_texte_a_filtrer
                plateau_ligne_texte_universel = plateau.plateau_ligne_texte_universel
                # Consulter la résolution du plateau
                self._chrono.start()
                resolution = ResoudrePlateau(plateau,
                                            repertoire_solution=self._repertoire_solution_unitaire)
                difficulte = resolution.difficulte_qui_perd_gagne
                difficulte_json_key_str = str(difficulte)
                lg_solution = resolution.longueur_solution_qui_perd_gagne
                nb_chemins = resolution.nb_chemins
                # Filtrage des plateaux selon la qualité des solutions
                if self._difficulte_min <= difficulte <= self._difficulte_max \
                    and lg_solution >= self._nb_coups_min \
                    and nb_chemins >= self._nb_chemins_min:
                    if difficulte_json_key_str not in dict_difficulte:
                        dict_difficulte[difficulte_json_key_str] = []
                        if verifier_deja_fait:
                            verifier_deja_fait = False
                            deja_fait = False
                            # Nouvelle difficulté ==> plateau jamais vu ==> recherche à poursuivre
                    if plateau_ligne_texte_universel not in dict_difficulte[difficulte_json_key_str]:
                        dict_difficulte[difficulte_json_key_str].append(plateau_ligne_texte_universel)
                        if verifier_deja_fait:
                            verifier_deja_fait = False
                            deja_fait = False
                            # Nouveau plateau ==> recherche à poursuivre
                    else:
                        if verifier_deja_fait:
                            verifier_deja_fait = False
                            deja_fait = True
                            # Plateau connu ==> Sortir de la recherche qui a deja été réalisée
                            self._chrono.pause()
                            break
                nb_plateaux_traites += 1
                self._chrono.pause()
            logger.info(f"Traitement {self._nom_tache} en {self._chrono} secondes")
            if deja_fait:
                logger.info("Filtrage des solutions QUI_PERD_GAGNE deja realise")
            else:
                logger.info("Filtrage des solutions QUI_PERD_GAGNE")
                self.ordonner_difficulte(solutions_classees["liste difficulte des plateaux"])
                solutions_classees_json.forcer_export(solutions_classees)
                logger.info("Export termine")
        else:
            logger.info(" - Ce lot de plateaux n'est pas encore termine, pas de classement de solutions.")


if __name__ == "__main__":
    NOM_TACHE = 'classer_les_solutions_qui_perd_gagne'
    if Path().parent.resolve().name == 'color_sort_for_anna_tools':
        # DEBUG
        FICHIER_JOURNAL = Path('logs') / f'{NOM_TACHE}.log'
        FICHIER_ANALYSE = Path('Pipelines') / 'pipeline_6_fusion_filtre_doublons_permutation_jetons_piles'
        FICHIER_SOLUTION_UNITAIRE = Path('Pipelines') / 'pipeline_7_solutions_unitaires'
        FICHIER_SOLUTION = Path('Pipelines') / 'pipeline_7_solutions'
    elif Path().parent.resolve().name == (Path('color_sort_for_anna_tools') / 'sources' / 'pipeline').name:
        FICHIER_JOURNAL = Path('..') / '..' / 'logs' / f'{NOM_TACHE}.log'
        FICHIER_ANALYSE = Path('..') / '..' / 'Pipelines' / 'pipeline_6_fusion_filtre_doublons_permutation_jetons_piles'
        FICHIER_SOLUTION_UNITAIRE = Path('..') / '..' / 'Pipelines' / 'pipeline_7_solutions_unitaires'
        FICHIER_SOLUTION = Path('..') / '..' / 'Pipelines' / 'pipeline_7_solutions'
    else:
        print("Impossible de déterminer le chemin des fichiers en mode debug ou release.")
        exit(1)

    # Configurer le logger
    if not FICHIER_JOURNAL.parent.exists():
        FICHIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    classer_solutions = FiltrerLesSolutionsQuiPerdGagne(
        nb_colonnes=range(2, 12),
        nb_lignes=range(2, 14),
        nb_colonnes_vides=1,
        gameplay='QUI_PERD_GAGNE',
        repertoire_analyse=str(FICHIER_ANALYSE),
        repertoire_solution_unitaire=str(FICHIER_SOLUTION_UNITAIRE),
        repertoire_solution=str(FICHIER_SOLUTION),
        nb_coups_min=3,
        difficulte_min=1,
        difficulte_max=99,
        nb_chemins_min=10,
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL,
        periode_scrutation_secondes = 1 * 60 * 60 # 1h
    )
    # classer_solutions.chercher_en_sequence()
    classer_solutions.afficher_enregistrer_synthese()
    #classer_solutions.chercher_en_boucle()
