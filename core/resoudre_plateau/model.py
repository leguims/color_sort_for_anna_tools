"Module pour creer, resoudre et qualifier les solutions des plateaux de 'ColorWoordSort'"
import copy

from core.plateau import Plateau
from io_utils.export_json import ExportJSON

class ResoudrePlateau:
    "Classe de resolution d'un plateau par parcours de toutes les possibilites de choix"
    def __init__(self,
                 plateau_initial: Plateau,
                 repertoire_solution):
        self._plateau_initial = copy.deepcopy(plateau_initial)
        # Statistiques des solutions:
        #    {
        #        "plateau": "AAAB.BB  .AB  ",
        #        # key = longueur de la solution
        #        # value = nombre de solutions de cette longueur
        #        "dico des longueurs": {3: 12, 4: 24},
        #        # Produit des choix à chaque étape de la solution la plus courte / rapporté à la taille du plateau
        #        # coup 1 = 3 choix, coup 2 = 2 choix et coup 3 = 1 choix
        #        # difficulté = 3x2x1 * (12x12) / (3 x 4)
        #        "difficulte": 72,
        #        "solution": []
        #    }
        # Les longueurs sont toutes egales (courtes et longues).
        # La difficulté dépend de :
        #   - Le nombre de choix
        #   - La taille du plateau.
        self._dico_des_longueurs = {}
        self._recherche_terminee = False
        self._difficulte = None
        self._solution = None

        self._liste_des_choix_possibles = None
        self._liste_plateaux_gagnants = None

        nom_plateau = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial._nb_lignes}"
        nom_solution = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial._nb_lignes}_Resolution_{self._plateau_initial.plateau_ligne_texte.replace(' ', '-')}"
        self._export_json_solutions = ExportJSON(delai=60, longueur=100,
                                                 nom_plateau=nom_plateau,
                                                 nom_export=nom_solution,
                                                 repertoire = repertoire_solution)
        from .io import importer_fichier_json
        importer_fichier_json(self)

    def __len__(self) -> int:
        "La longueur de la solution definit la difficulte"
        # Le nombre de solution n'a pas d'incidence sur la difficulte
        return len(self._solution) if self._solution else 0

    def to_dict(self) -> dict:
        from .io import to_dict
        return to_dict(self)

    @property
    def difficulte(self) -> int | None:
        from .heuristics import difficulte
        return difficulte(self)

    # API io
    def exporter_fichier_json(self) -> None:
        from .io import exporter_fichier_json
        exporter_fichier_json(self)

    def importer_fichier_json(self) -> None:
        from .io import importer_fichier_json
        importer_fichier_json(self)

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
    def est_valide(self, plateau: Plateau, choix) -> bool:
        from .validation import est_valide
        return est_valide(plateau, choix)

    def ensemble_des_plateaux_gagnants(self) -> list:
        from .validation import ensemble_des_plateaux_gagnants
        return ensemble_des_plateaux_gagnants(self)

    def solution_complete(self, plateau: Plateau) -> bool:
        from .validation import solution_complete
        return solution_complete(self, plateau)

    # API resolution
    def backtracking(self, plateau: Plateau = None, liste_des_choix_courants = None, profondeur_recursion = None) -> None:
        from .resolution import backtracking
        return backtracking(self, plateau, liste_des_choix_courants, profondeur_recursion)

    # def enregistrer_solution(self, liste_des_choix_courants) -> None:
    #     from .resolution import enregistrer_solution
    #     enregistrer_solution(self, liste_des_choix_courants)
