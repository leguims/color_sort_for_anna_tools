"""Parcourt les plateaux resolus et les rassemble par GAMEPLAY dans un fichier dédié.
Les plateaux sont dans une écriture universelle avec les attributs spécifiques liés au GAMEPLAY.
Entrée : 'pipeline_5_filtre_doublons_permutation_jetons_piles'
Entrée : 'pipeline_6_solutions_unitaires'
Sortie : '7_filtrer_les_solutions_CLASSIQUE_pour_godot'"""

import datetime
import time
import logging
from pathlib import Path
import random

import sys

# Allow this script to run directly from any working directory.
REPERTOIRE_SOURCES = Path(__file__).resolve().parent.parent
if str(REPERTOIRE_SOURCES) not in sys.path:
    sys.path.insert(0, str(REPERTOIRE_SOURCES))

from core.plateau import Plateau
from core.lot_de_plateaux import LotDePlateaux
from core.resoudre_plateau import ResoudrePlateau
from io_utils.profiler_le_code import ProfilerLeCode
from io_utils.export_json import ExportJSON
from io_utils.chrono import Chrono

class FiltrerLesSolutionsClassique:
    """Parcourt les plateaux resolus et les rassemble dans le fichier
    'Solutions_classees.json' par difficulte avec une ecriture universelle"""
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                gameplay,
                repertoire_analyse,
                repertoire_solution_unitaire,
                repertoire_solution,
                nb_coups_min,
                difficulte_min,
                difficulte_max,
                nb_chemins_min,
                nom_tache,
                fichier_journal,
                profiler_le_code = False,
                periode_scrutation_secondes = 30*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._gameplay = gameplay
        self._repertoire_analyse = repertoire_analyse
        self._repertoire_solution_unitaire = repertoire_solution_unitaire
        self._repertoire_solution = repertoire_solution
        self._fichier_solution = f'8_filtrer_les_solutions_{self._gameplay}_pour_godot'
        self._fichier_repartition = f'8_repartition_des_solutions_{self._gameplay}_pour_godot'
        self._solutions_classees = {}
        self._plateau = Plateau(1, 1, 1)
        self._nb_coups_min = nb_coups_min
        self._difficulte_min = difficulte_min
        self._difficulte_max = difficulte_max
        self._nb_chemins_min = nb_chemins_min
        self._nom_tache = nom_tache
        self._fichier_journal = fichier_journal
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._profiler_le_code = profiler_le_code
        self._periode_scrutation_secondes = periode_scrutation_secondes
        self._chrono = Chrono()
        # Configurer le logger
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._logger = logging.getLogger(f"{self._nom_tache}")

    @property
    def elapsed(self):
        return self._chrono.elapsed

    def classer_et_exporter_les_solutions(self, colonnes, lignes):
        self._logger = logging.getLogger(f"{colonnes}.{lignes}.{self._nom_tache}")
        self._logger.info(f"DEBUT {self._nom_tache}")
        # logger.info(plateau.plateau_ligne_texte_universel)
        self._plateau = Plateau(colonnes, lignes, self._nb_colonnes_vides)
        lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse)
        if lot_de_plateaux.est_deja_termine:
            self._logger.info("Ce lot de plateaux est termine")

            self._logger.info(f"Importer les solutions {self._gameplay}")
            solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='',
                                                 nom_export=self._fichier_solution,
                                                 repertoire=self._repertoire_solution)
            self._solutions_classees = solutions_classees_json.importer()

            if "liste difficulte des plateaux" not in self._solutions_classees:
                self._solutions_classees["liste difficulte des plateaux"] = {}

            # Vérifier si ce type de plateau est deja present dans le fichier
            # Le premier enregistrement est vérifié.
            verifier_deja_fait = True
            deja_fait = False
            # Trace pour l'avancement de la tache
            self._logger.info(f"Nombre de plateau a parcourir : {lot_de_plateaux.nb_plateaux_valides}")
            nb_plateaux_traites = 0
            avancement_affichage = {pourcentage: False for pourcentage in range(10, 100, 5)}
            self._logger.info(f"Regle : {self._difficulte_min}<difficulte<{self._difficulte_max}, lg_solution>={self._nb_coups_min}, nb_chemins>={self._nb_chemins_min}.")
            # Parcourir chaque solution et remplir la structure de données
            for plateau_ligne_texte_a_filtrer in lot_de_plateaux.plateaux_valides:
                avancement = round(100. * nb_plateaux_traites / lot_de_plateaux.nb_plateaux_valides)
                if avancement in avancement_affichage and not avancement_affichage.get(avancement, True):
                    avancement_affichage[avancement] = True
                    self._logger.info(f"Avancement : {avancement}%")

                # Traitement unitaire par plateau
                self._chrono.start()
                self._plateau.clear()
                self._plateau.plateau_ligne_texte = plateau_ligne_texte_a_filtrer
                deja_fait = self.classer_et_exporter_la_solution_pour_godot(verifier_deja_fait)
                if deja_fait:
                    # Plateau connu ==> Sortir de la recherche qui a deja été réalisée
                    break

                nb_plateaux_traites += 1
                if verifier_deja_fait:
                    verifier_deja_fait = False
                self._chrono.pause()
            self._logger.info(f"Traitement {self._nom_tache} en {self._chrono} secondes")
            if deja_fait:
                self._logger.info(f"Filtrage des solutions {self._gameplay} deja realise")
            else:
                self._logger.info(f"Filtrage des solutions {self._gameplay}")
                self.ordonner_difficulte(self._solutions_classees["liste difficulte des plateaux"])
                solutions_classees_json.forcer_export(self._solutions_classees)
                self._logger.info("Export termine")
        else:
            self._logger.info(" - Ce lot de plateaux n'est pas encore termine, pas de classement de solutions.")

    def classer_et_exporter_la_solution_pour_godot(self, verifier_deja_fait = False):
        # self._logger.info(self._plateau.plateau_ligne_texte_universel)
        deja_fait = False
        plateau_ligne_texte_universel = self._plateau.plateau_ligne_texte_universel
        # Consulter la résolution du plateau
        resolution = ResoudrePlateau(self._plateau,
                                    repertoire_solution=self._repertoire_solution_unitaire)
        difficulte = resolution.difficulte(self._gameplay)
        difficulte_json_key_str = f"{int(difficulte):03d}"
        lg_solution = resolution.longueur_solution(self._gameplay)
        nb_chemins = resolution.nb_chemins
        # Filtrage des plateaux selon la qualité des solutions
        if self._difficulte_min <= difficulte <= self._difficulte_max \
            and lg_solution >= self._nb_coups_min \
            and nb_chemins >= self._nb_chemins_min:

            self._logger.info(f"{self._plateau.plateau_ligne_texte_universel} ACCEPTE : difficulte={difficulte}, lg_solution={lg_solution}, nb_chemins={nb_chemins}.")

            dict_difficulte = self._solutions_classees["liste difficulte des plateaux"]
            if difficulte_json_key_str not in dict_difficulte:
                dict_difficulte[difficulte_json_key_str] = []
            if plateau_ligne_texte_universel not in dict_difficulte[difficulte_json_key_str]:
                # Plateau au format GODOT
                plateau_classique = {
                    "nom": plateau_ligne_texte_universel,
                    "difficulte": difficulte,
                    "gameplay": self._gameplay
                    }
                dict_difficulte[difficulte_json_key_str].append(plateau_classique)
            elif verifier_deja_fait:
                # Plateau connu ==> Sortir de la recherche qui a deja été réalisée
                deja_fait = True
        else:
            self._logger.info(f"{self._plateau.plateau_ligne_texte_universel} REFUSE : difficulte={difficulte}, lg_solution={lg_solution}, nb_chemins={nb_chemins}.")
        return deja_fait

    # Copie de 'LotDePlateaux.arret_des_enregistrements_de_difficultes_plateaux()'
    def ordonner_difficulte(self, ensemble_des_difficultes_de_plateaux):
        "Methode qui classe les difficultes des solutions"
        # Classement des difficultes
        cles_difficulte = list(ensemble_des_difficultes_de_plateaux.keys())
        if None in cles_difficulte:
            cles_difficulte.remove(None) # None est inclassable avec 'list().sort()'
        try:
            cles_difficulte.sort()
        except TypeError as e:
            print(f"TypeError : ensemble_des_difficultes_de_plateaux: {ensemble_des_difficultes_de_plateaux}")
            print(f"TypeError : cles_difficulte: {cles_difficulte}")
            raise TypeError(f"TypeError : cles_difficulte: {cles_difficulte}")
        dico_difficulte_classe = {k: ensemble_des_difficultes_de_plateaux[k] for k in cles_difficulte}
        if None in ensemble_des_difficultes_de_plateaux:
            dico_difficulte_classe[None] = ensemble_des_difficultes_de_plateaux[None]
        ensemble_des_difficultes_de_plateaux.clear()
        ensemble_des_difficultes_de_plateaux.update(dico_difficulte_classe)

    def afficher_enregistrer_synthese(self):
        self._logger.info(f"*** Synthese des Solutions {self._gameplay}:")
        solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=self._fichier_solution, repertoire=self._repertoire_solution)
        solutions_classees = solutions_classees_json.importer()

        if solutions_classees.get('liste difficulte des plateaux'):
            repartition = dict()
            repartition['gameplay'] = self._gameplay
            somme_plateaux = 0
            for difficulte, liste_plateaux in solutions_classees.get('liste difficulte des plateaux', {}).items():
                self._logger.info(f" - Difficulte : {difficulte} : {len(liste_plateaux)} plateau{self.pluriel(liste_plateaux, 'x')}")
                if difficulte:
                    somme_plateaux += len(liste_plateaux)
                    repartition[f"{int(difficulte):03d}"] = f"{len(liste_plateaux):_}".replace("_", ".")
            self._logger.info(f" - Total : {somme_plateaux} plateau{self.pluriel(range(somme_plateaux), 'x')} valide{self.pluriel(range(somme_plateaux), 's')}")
            repartition['total'] = f"{somme_plateaux:_}".replace("_", ".")
            self.ordonner_difficulte(repartition)
            repartition_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=self._fichier_repartition, repertoire=self._repertoire_solution)
            repartition_json.forcer_export(repartition)

    def pluriel(self, LIGNES, lettre='s'):
        return lettre if len(LIGNES) > 1 else ""

    def chercher_en_boucle(self):
        # Configurer le logger
        self._logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")

        while(True):
            self._logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
            # Parcourir aléatoirement pour pouvoir lancer plusieurs solutions en parallele.
            liste_colonne_ligne = [{'colonnes':c, 'lignes':l} for c in self._nb_colonnes for l in self._nb_lignes]
            random.shuffle(liste_colonne_ligne)
            taille_tache = len(liste_colonne_ligne)
            for colonne_ligne in liste_colonne_ligne:
                indice = liste_colonne_ligne.index(colonne_ligne) + 1
                print(f"Famille courante :  : {colonne_ligne.get('colonnes')}x{colonne_ligne.get('lignes')} avancement {indice}/{taille_tache}")
                self.classer_et_exporter_les_solutions(colonne_ligne.get('colonnes'), colonne_ligne.get('lignes'))
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            self._logger.info(f"{current_time} - Attente entre 2 iterations de {self._periode_scrutation_secondes}s...")
            time.sleep(self._periode_scrutation_secondes)

    def chercher_en_sequence(self):
        profil = ProfilerLeCode('chercher_en_sequence', self._profiler_le_code)
        profil.start()

        # Pas d'effacement, cumulation des différentes recherches.
        # # Effacer l'existant
        # solutions_classees_json = ExportJSON(0, 0, '', nom_export=self._fichier_solution, repertoire=self._repertoire_solution)
        # solutions_classees_json.effacer()
        
        # Configurer le logger
        self._logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        self._logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        # Parcourir aléatoirement pour pouvoir lancer plusieurs solutions en parallele.
        liste_colonne_ligne = [{'colonnes':c, 'lignes':l} for c in self._nb_colonnes for l in self._nb_lignes]
        random.shuffle(liste_colonne_ligne)
        taille_tache = len(liste_colonne_ligne)
        for colonne_ligne in liste_colonne_ligne:
            indice = liste_colonne_ligne.index(colonne_ligne) + 1
            print(f"Famille courante :  : {colonne_ligne.get('colonnes')}x{colonne_ligne.get('lignes')} avancement {indice}/{taille_tache}")
            self.classer_et_exporter_les_solutions(colonne_ligne.get('colonnes'), colonne_ligne.get('lignes'))
        profil.stop()

        self.afficher_enregistrer_synthese()
        self._logger.info('-'*10 + " FIN " + '-'*10)

if __name__ == "__main__":
    NOM_TACHE = 'classer_les_solutions_classique'
    NOM_DEPOT = 'color_sort_for_anna_tools'
    if Path().parent.resolve().name == NOM_DEPOT:
        # DEBUG
        FICHIER_JOURNAL = Path('logs') / f'{NOM_TACHE}.log'
        FICHIER_ANALYSE = Path('Pipelines') / 'pipeline_6_fusion_filtre_doublons_permutation_jetons_piles'
        FICHIER_SOLUTION_UNITAIRE = Path('Pipelines') / 'pipeline_7_solutions_unitaires'
        FICHIER_SOLUTION = Path('Pipelines') / 'pipeline_7_solutions'
    elif Path().parent.resolve().name == (Path(NOM_DEPOT) / 'sources' / 'pipeline').name:
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

    classer_solutions = FiltrerLesSolutionsClassique(
        nb_colonnes=range(2, 12),
        nb_lignes=range(2, 14),
        nb_colonnes_vides=1,
        gameplay='CLASSIQUE',
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
    classer_solutions.chercher_en_sequence()
    #classer_solutions.afficher_enregistrer_synthese()
    #classer_solutions.chercher_en_boucle()
