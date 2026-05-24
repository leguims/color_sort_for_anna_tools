"Module pour itérer les plateaux"
from itertools import product
import logging

from core.plateau import Plateau
from .model import LotDePlateaux
from .generator import construire_les_permutations_de_jetons, \
                    construire_les_permutations_de_colonnes

# TODO : Gerer la memoire si necessaire (self._ensemble_des_plateaux_a_ignorer)

class IterPlateau:
    """Classe qui gere l'itération dans tous les plateaux possibles."""
    def __init__(self, dim_plateau: tuple[int, int, int], lot_de_plateaux: LotDePlateaux):
        # Plateau de base
        self._plateau = Plateau(dim_plateau[0], dim_plateau[1], dim_plateau[2])
        self._lot_de_plateau = lot_de_plateaux

        # Gestion du lot de plateau
        self._ensemble_des_plateaux_valides = set() # Plateaux valides collectés dans la recherche.
        self._ensemble_des_plateaux_a_ignorer = set() # Plateaux invalides collectés dans la recherche.
        self._iter_courante = None  # Initialisation de la permutation courante
        self._iter_iterateur = None  # Initialisation de l'itérateur de permutations
        self._logger = logging.getLogger(f"{self._plateau.nb_colonnes}.{self._plateau.nb_lignes}.{IterPlateau.__name__}")
        self.__iter__()

    # Iterateur avec : __iter__ et __next__
    def __iter__(self):
        self.logger.debug(f"__iter__ : Initialisation de l'itérateur.")
        self._iter_iterateur = product(self._plateau.liste_familles + [self._plateau.case_vide],
                                       repeat=self._plateau.nb_colonnes * self._plateau.nb_lignes) 
        return self

    def __next__(self):
        self.logger.debug(f"__next__ : Itération dans les permutations.")
        valide_et_interessant = False
        while not valide_et_interessant:
            # Itérer avec les 'product'
            self._iter_courante = next(self._iter_iterateur)
            self.logger.debug(f"__next__ : {self._iter_courante}.")
            if self.plateau_est_connu(''.join(self._iter_courante)):
                raise StopIteration
            valide_et_interessant = self.plateau_est_valide_et_interessant(''.join(self._iter_courante))
        return self._plateau

    def plateau_est_connu(self, permutation_plateau: str) -> bool:
        "Retourne 'True' si le plateau est deja connu (répétition)"
        return permutation_plateau in self._ensemble_des_plateaux_valides
    
    def plateau_est_valide_et_interessant(self, permutation_plateau: str) -> bool:
        "Retourne 'True' si le plateau est valide"
        if permutation_plateau in self._ensemble_des_plateaux_a_ignorer:
            # Ignorer et oublier ce plateau
            self._ensemble_des_plateaux_a_ignorer.discard(permutation_plateau)
            return False

        if permutation_plateau not in self._ensemble_des_plateaux_valides:
            self._plateau.clear()
            self._plateau.plateau_ligne_texte = permutation_plateau
            # Verifier que la plateau est valide
            if self._plateau.est_valide and self._plateau.est_interessant:
                # Enregistrer la permutation courante qui est un nouveau plateau valide
                self._ensemble_des_plateaux_valides.add(permutation_plateau)
                # Ajouter toutes les permutations possibles de ce plateau valide à l'ensemble des plateaux à ignorer
                for permutation_plateau_a_ignorer in construire_les_permutations_de_colonnes(self._lot_de_plateau, self._plateau):
                    # Filtrer permutations piles
                    self._ensemble_des_plateaux_a_ignorer.add(permutation_plateau_a_ignorer.plateau_ligne_texte)
            return True
        return False

    def __len__(self) -> int:
        return self.nb_plateaux_valides

    @property
    def logger(self) -> logging.Logger:
        "Logger"
        return self._logger

    @property
    def plateau(self) -> Plateau:
        "Plateau courant"
        return self._plateau

    @property
    def plateaux_valides(self) -> set:
        "Ensemble des plateaux valides"
        return self._ensemble_des_plateaux_valides

    @property
    def nb_plateaux_valides(self) -> int:
        "Nombre de plateaux valides"
        return len(self._ensemble_des_plateaux_valides)

    @property
    def nb_plateaux_ignores(self) -> int:
        "Nombre de plateaux ignores"
        return len(self._ensemble_des_plateaux_a_ignorer)
