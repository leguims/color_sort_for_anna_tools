"Module pour creer, resoudre et qualifier les solutions des plateaux de 'ColorWoordSort'"
import copy

from core.plateau import Plateau
from io_utils.export_json import ExportJSON

class ResoudrePlateau:
    "Classe de resolution d'un plateau par parcours de toutes les possibilites de choix"
    def __init__(self,
                 plateau_initial: Plateau,
                 repertoire_solution: str):
        self._plateau_initial = copy.deepcopy(plateau_initial)
        # Statistiques des solutions: voir io.py
        self._dico_des_longueurs_de_solutions : dict[str, int] = {}
        self._dico_des_longueurs_de_blocages : dict[str, int] = {}
        self._recherche_terminee = False
        self._difficulte_classique = -1
        self._difficulte_qui_perd_gagne = -1
        self._solution = []

        self._liste_des_choix_possibles = []
        self._liste_plateaux_gagnants = []

        nom_plateau = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial.nb_lignes}"
        nom_solution = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial.nb_lignes}_Resolution_{self._plateau_initial.plateau_ligne_texte.replace(' ', '-')}"
        self._export_json_solutions: ExportJSON = ExportJSON(delai=60, longueur=100,
                                                 nom_plateau=nom_plateau,
                                                 nom_export=nom_solution,
                                                 repertoire = repertoire_solution)
        from .io import importer_fichier_json
        importer_fichier_json(self)

    def __len__(self) -> int:
        "La longueur de la solution la plus courte"
        return len(self._solution) if self._solution else 0

    def to_dict(self) -> dict:
        from .io import to_dict
        return to_dict(self)

    @property
    def difficulte_classique(self) -> int:
        from .heuristics import difficulte_classique
        return difficulte_classique(self)

    @property
    def difficulte_qui_perd_gagne(self) -> int:
        from .heuristics import difficulte_qui_perd_gagne
        return difficulte_qui_perd_gagne(self)

    @property
    def longueur_solution_classique(self) -> int:
        if not self._dico_des_longueurs_de_solutions:
            return 0
        return min([int(k) for k in self._dico_des_longueurs_de_solutions.keys()])

    @property
    def longueur_solution_qui_perd_gagne(self) -> int:
        if not self._dico_des_longueurs_de_blocages:
            return 0
        return min([int(k) for k in self._dico_des_longueurs_de_blocages.keys()])

    @property
    def nb_solution_classique(self) -> int:
        if not self._dico_des_longueurs_de_solutions:
            return 0
        return sum([v for v in self._dico_des_longueurs_de_solutions.values()])

    @property
    def nb_solution_qui_perd_gagne(self) -> int:
        if not self._dico_des_longueurs_de_blocages:
            return 0
        return sum([v for v in self._dico_des_longueurs_de_blocages.values()])

    @property
    def nb_branches(self) -> int:
        return self.nb_solution_classique + self.nb_solution_qui_perd_gagne

    # API io
    # def exporter_fichier_json(self) -> None:
    #     from .io import exporter_fichier_json
    #     exporter_fichier_json(self)

    # def importer_fichier_json(self) -> None:
    #     from .io import importer_fichier_json
    #     importer_fichier_json(self)

    # API choix
    # def ensemble_des_choix_possibles(self) -> list:
    #     from .choix import ensemble_des_choix_possibles
    #     return ensemble_des_choix_possibles(self)

    # def ajouter_choix(self, plateau: Plateau, liste_des_choix_courants, choix) -> None:
    #     from .choix import ajouter_choix
    #     ajouter_choix(plateau, liste_des_choix_courants, choix)

    # def retirer_choix(self, plateau: Plateau, liste_des_choix_courants, choix) -> None:
    #     from .choix import retirer_choix
    #     retirer_choix(plateau, liste_des_choix_courants, choix)

    # API validation
    # def choix_est_valide(self, plateau: Plateau, choix) -> bool:
    #     from .validation import choix_est_valide
    #     return choix_est_valide(plateau, choix)

    # def ensemble_des_plateaux_gagnants(self) -> list:
    #     from .validation import ensemble_des_plateaux_gagnants
    #     return ensemble_des_plateaux_gagnants(self)

    # def solution_complete(self, plateau: Plateau) -> bool:
    #     from .validation import solution_complete
    #     return solution_complete(self, plateau)

    # API resolution
    def backtracking(self, plateau: Plateau = None, liste_des_choix_courants = None, profondeur_recursion = None) -> None:
        from .resolution import backtracking
        return backtracking(self, plateau, liste_des_choix_courants, profondeur_recursion)

    # def enregistrer_solution(self, liste_des_choix_courants) -> None:
    #     from .resolution import enregistrer_solution
    #     enregistrer_solution(self, liste_des_choix_courants)
