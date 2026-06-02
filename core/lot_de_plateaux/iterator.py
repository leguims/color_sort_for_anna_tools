"Module pour itérer les plateaux"
from itertools import product
import logging
import copy
import datetime

from core.plateau import Plateau
from .model import LotDePlateaux
from .generator import construire_les_permutations_de_jetons, \
                    construire_les_permutations_de_colonnes

# TODO : Gerer la memoire si necessaire (self._ensemble_des_plateaux_a_ignorer)

class IterPlateau:
    """Classe qui gere l'itération dans tous les plateaux possibles."""
    def __init__(self, dim_plateau: tuple[int, int, int], delai_affichage : int, lot_de_plateaux: LotDePlateaux):
        # Plateau de base
        self._plateau = Plateau(dim_plateau[0], dim_plateau[1], dim_plateau[2])
        self.plateau.creer_plateau_initial()
        self._lot_de_plateau = lot_de_plateaux
        self._delai_affichage = delai_affichage
        self._dernier_affichage = 0.

        # Gestion du lot de plateau
        self._ensemble_des_plateaux_valides_initiaux = copy.deepcopy(lot_de_plateaux._ensemble_des_plateaux_valides) # Copie des plateaux valides connus
        self._ensemble_des_plateaux_valides = set() # Plateaux valides collectés dans la recherche.
        self._ensemble_des_plateaux_a_ignorer = set() # Plateaux invalides collectés dans la recherche.
        self._iter_courante = None  # Initialisation de la permutation courante
        self._iter_iterateur = None  # Initialisation de l'itérateur de permutations

        # Recherche terminé
        self._iter_index = 0        # Initialisation de l'index pour les recherches terminées
        self._iter_index_max = 0    # Initialisation de l'index max. pour les recherches terminées
        self._iter_list = []    # Liste des plateaux valides

        self._logger = logging.getLogger(f"{self.plateau.nb_colonnes}.{self.plateau.nb_lignes}.{IterPlateau.__name__}")
        self.__iter__()

    # Iterateur avec : __iter__ et __next__
    def __iter__(self):
        self.logger.debug(f"__iter__ : Initialisation de l'itérateur.")
        if self._lot_de_plateau.est_deja_termine:
            self.logger.debug(f"__iter__ : est_deja_termine.")
            # Parcourir les plateaux valides
            self._iter_index = 0  # Réinitialisation de l'index de l'itérateur
            self._iter_index_max = len(self._lot_de_plateau.plateaux_valides_liste_classee)
            self._iter_list = self._lot_de_plateau.plateaux_valides_liste_classee
        else:
            self.logger.debug(f"__iter__ : NOT est_deja_termine.")
            self._iter_iterateur = product(self.plateau.liste_familles + [self.plateau.case_vide],
                                       repeat=self.plateau.nb_colonnes * self.plateau.nb_lignes) 
        return self

    def __next__(self):
        if self._lot_de_plateau.est_deja_termine:
            self.logger.debug(f"__next__ : est_deja_termine.")
            # Parcourir les plateaux valides
            if self._iter_index < self._iter_index_max:
                self._iter_index += 1
                self.plateau.clear()
                self.plateau.plateau_ligne_texte = self._iter_list[self._iter_index - 1]
                return self.plateau
            raise StopIteration
        else:
            self.logger.debug(f"__next__ : NOT est_deja_termine.")
            # Phase 1 : Avancer dans les iterations de plateaux deja connus
            if self._ensemble_des_plateaux_valides_initiaux:
                self.__next__recherche_libre_phase_1()

            # Phase 2 : Avancer dans les iterations de plateaux deja cherchés
            if self._lot_de_plateau._recherche_dernier_plateau:
                self.__next__recherche_libre_phase_2()

            return self.__next__recherche_libre_phase_3()

    def __next__recherche_libre_phase_1(self):
        # Phase 1 : Avancer dans les iterations de plateaux deja connus
        if self._ensemble_des_plateaux_valides_initiaux:
            self.logger.info(f"__next__ : Reprise phase 1 debutee.")
            while self._ensemble_des_plateaux_valides_initiaux:
                self._iter_courante = next(self._iter_iterateur)
                plateau_ligne_texte = ''.join(self._iter_courante)
                self._enregistrer_plateau_courant(plateau_ligne_texte)
                # self.logger.info(f"__next__ : Epuisement : iteration courante = '{self.plateau.plateau_ligne_texte_universel}'.")
                self._afficher_periodiquement_iterateur()
                try:
                    self._ensemble_des_plateaux_valides_initiaux.remove(plateau_ligne_texte)
                    # Pas d'exception = Le plateau valide est trouvé
                    if self.plateau_valide(plateau_ligne_texte):
                        self.logger.info(f"__next__ : Epuisement des plateaux connus restants : {len(self._ensemble_des_plateaux_valides_initiaux)}.")
                        return self.plateau 
                except KeyError:
                    pass
            self.logger.info(f"__next__ : Reprise phase 1 terminee.")

    def __next__recherche_libre_phase_2(self):
        # Phase 2 : Avancer dans les iterations de plateaux deja cherchés
        if self._lot_de_plateau._recherche_dernier_plateau:
            self.logger.info(f"__next__ : Reprise phase 2 debutee.")

            plateau_reprise_ligne_texte_universel = self._lot_de_plateau._recherche_dernier_plateau
            plateau_reprise_ligne_texte = plateau_reprise_ligne_texte_universel.replace('.','')
            self.logger.info(f"__next__ : Reprise : derniere iteration = '{plateau_reprise_ligne_texte_universel}'.")

            while plateau_reprise_ligne_texte_universel != self.plateau.plateau_ligne_texte_universel:
                self._iter_courante = next(self._iter_iterateur)
                plateau_ligne_texte = ''.join(self._iter_courante)
                self._enregistrer_plateau_courant(plateau_ligne_texte)

            # Traiter le plateau de reprise
            if self.plateau_connu(plateau_reprise_ligne_texte):
                self.logger.debug(f"__next__ : StopIteration.")
                raise StopIteration
            valide = self.plateau_valide(plateau_reprise_ligne_texte)
            if valide:
                return self.plateau
            self.logger.info(f"__next__ : Reprise phase 2 terminee.")

    def __next__recherche_libre_phase_3(self):
        valide = False
        while not valide:
            # Itérer avec les 'product'
            self._iter_courante = next(self._iter_iterateur)
            plateau_ligne_texte = ''.join(self._iter_courante)
            self._enregistrer_plateau_courant(plateau_ligne_texte)
            # self.logger.info(f"__next__ : Recherche : derniere iteration = '{self.plateau.plateau_ligne_texte_universel}'.")

            self._afficher_periodiquement_iterateur()

            # Enregistrer l'iteration pour la reprise
            self._lot_de_plateau._recherche_dernier_plateau = self.plateau.plateau_ligne_texte_universel
            enregistre = self._lot_de_plateau._export_json.exporter(self._lot_de_plateau)
            if enregistre:
                self.logger.info(f"__next__ : Recherche : enregistre la reprise '{self.plateau.plateau_ligne_texte_universel}'.")

            if self.plateau_connu(plateau_ligne_texte):
                self.logger.debug(f"__next__ : StopIteration.")
                raise StopIteration
            valide = self.plateau_valide(plateau_ligne_texte)
        return self.plateau

    def _afficher_periodiquement_iterateur(self):
        # Log pour suivre l'avancement.
        if datetime.datetime.now().timestamp() - self._dernier_affichage > self._delai_affichage:
            self.logger.info(f"iteration ='{self.plateau.plateau_ligne_texte_universel}'")
            self._dernier_affichage  = datetime.datetime.now().timestamp()

    def plateau_connu(self, permutation_plateau: str) -> bool:
        "Retourne 'True' si le plateau est deja connu (repetition)"
        return permutation_plateau in self._ensemble_des_plateaux_valides

    def plateau_valide(self, permutation_plateau: str) -> bool:
        "Retourne 'True' si le plateau est valide (à remonter)"
        if permutation_plateau in self._ensemble_des_plateaux_a_ignorer:
            # Ignorer et oublier ce plateau
            self._ensemble_des_plateaux_a_ignorer.discard(permutation_plateau)
            return False

        self._enregistrer_plateau_courant(permutation_plateau)
        # Verifier que la plateau est valide
        if self.plateau.est_valide and self.plateau.est_interessant:
            # Enregistrer la permutation courante qui est un nouveau plateau valide
            self._ensemble_des_plateaux_valides.add(permutation_plateau)
            # Ajouter toutes les permutations possibles de ce plateau valide à l'ensemble des plateaux à ignorer
            for permutation_plateau_a_ignorer in construire_les_permutations_de_colonnes(self._lot_de_plateau, self.plateau):
                # Filtrer permutations piles
                self._ensemble_des_plateaux_a_ignorer.add(permutation_plateau_a_ignorer.plateau_ligne_texte)
            return True
        return False

    def _enregistrer_plateau_courant(self, permutation_plateau: str):
        self.plateau.clear()
        self.plateau.plateau_ligne_texte = permutation_plateau

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
