"Module pour creer, resoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
import logging
from copy import deepcopy

from core.plateau import Plateau
from io_utils.export_json import ExportJSON

DELAI_AFFICHER_ITER_LOT_DE_PLATEAUX = 5*60

# TODO : reprendre l'enregistrement a partir du fichier. => Pas d'amelioration, essayer de comprendre.

class LotDePlateaux:
    """Classe qui gere les lots de plateaux pour parcourir l'immensite des plateaux existants.
Le chanmps nb_plateaux_max designe la memoire allouee pour optimiser la recherche."""
    def __init__(self, dim_plateau, repertoire_export_json, nb_plateaux_max = 1_000_000):
        # Plateau de base
        self._dim_plateau = dim_plateau
        self._plateau_courant = Plateau(dim_plateau[0], dim_plateau[1], dim_plateau[2])

        # Gestion du lot de plateau
        self._ensemble_des_plateaux_valides = set() # Plateaux valides collectés dans la recherche.
        self._iter_index = 0  # Initialisation de l'index de l'itérateur
        self._iter_index_max = 0
        self._recherche_terminee = False # Indique si la recherche de plateaux valides est terminee (exhaustive)
        self._recherche_dernier_plateau = None # Dernier plateau traité en recherche pour reprise


        self._ensemble_des_permutations_de_nombres = None # Ensemble constant utilisé pour les permutations de jetons
        self._nb_plateaux_max = nb_plateaux_max # Limite memoire pour la recherche (plateaux à ignorer)
        self._export_json: ExportJSON
        self._ensemble_des_difficultes_de_plateaux = {} # Ensemble des plateaux classés par difficulté et profondeur
        self._a_change = False # Indique si les données de la classe ont changé.
        self._logger = logging.getLogger(f"{self._plateau_courant.nb_colonnes}.{self._plateau_courant.nb_lignes}.{LotDePlateaux.__name__}")
        self._filtrer_plateaux_invalides_ou_ininteressants = False # Indique si la phase 1 de revalidation est terminee
        self._filtrer_doublons_permutation_jetons = False # Indique si la phase 2 de revalidation est terminee
        self._filtrer_doublons_permutation_piles = False # Indique si la phase 3 de revalidation est terminee
        self._filtrer_doublons_permutation_jetons_piles = False # Indique si la phase 4 de revalidation est terminee
        self._filtrer_dernier_plateau_traite = None # Dernier plateau traité en revalidation pour reprise

        # Reprise de la recherche
        self._repertoire_export_json = repertoire_export_json
        from .io import init_export_json, importer_fichier_json
        init_export_json(self)
        importer_fichier_json(self)

    # Iterateur avec : __iter__ et __next__
    def __iter__(self):
        if self.est_deja_termine:
            self.logger.debug(f"__iter__ : est_deja_termine.")
            # Parcourir les plateaux valides
            self._iter_index = 0  # Réinitialisation de l'index de l'itérateur
            self._iter_index_max = len(self.plateaux_valides_liste_classee)
            self._iter_list = self.plateaux_valides_liste_classee
        else:
            self.logger.debug(f"__iter__ : NOT est_deja_termine.")
            # Poursuivre la recherche de plateaux valides
            # TODO : Lire le dernier plateau traité pour reprendre la recherche à partir de ce plateau.
            from .iterator import IterPlateau
            self._iter_iterateur = IterPlateau(self._dim_plateau,
                                                DELAI_AFFICHER_ITER_LOT_DE_PLATEAUX,
                                                self)
        return self

    def __next__(self):
        if self.est_deja_termine:
            self.logger.debug(f"__next__ : est_deja_termine.")
            # Parcourir les plateaux valides
            if self._iter_index < self._iter_index_max:
                self._iter_index += 1
                self._plateau_courant.clear()
                self._plateau_courant.plateau_ligne_texte = self._iter_list[self._iter_index - 1]
                return self._plateau_courant.plateau_ligne_texte_universel
        else:
            self.logger.debug(f"__next__ : NOT est_deja_termine.")
            # Itérer avec les permutations
            try:
                self._plateau_courant = next(self._iter_iterateur)

                # Enregistrement du plateau courant pour une eventuelle reprise.
                self._recherche_dernier_plateau = self._plateau_courant.plateau_ligne_texte_universel
                self._export_json.exporter(self)
                return self._plateau_courant.plateau_ligne_texte_universel
            except StopIteration:
                self._ensemble_des_plateaux_valides = deepcopy(self._iter_iterateur.plateaux_valides)
                self.arret_des_enregistrements()
        raise StopIteration

    def __len__(self) -> int:
        return self.nb_plateaux_valides

    @property
    def logger(self) -> logging.Logger:
        "Logger"
        return self._logger

    @property
    def chemin_enregistrement(self):
        return self._export_json.chemin_enregistrement

    @property
    def plateaux_valides(self) -> set:
        "Ensemble des plateaux valides"
        return self._ensemble_des_plateaux_valides

    @property
    def plateaux_valides_liste_classee(self) -> list:
        "Liste classee des plateaux valides"
        liste_classee = list(self._ensemble_des_plateaux_valides)
        liste_classee.sort()
        return liste_classee

    @property
    def nb_plateaux_valides(self) -> int:
        "Nombre de plateaux valides"
        return len(self._ensemble_des_plateaux_valides)

    @property
    def difficulte_plateaux(self) -> dict:
        "Ensemble des difficultes de plateaux resolus"
        return self._ensemble_des_difficultes_de_plateaux

    @property
    def nb_plateaux_solutionnes(self) -> int:
        "Nombre de plateaux valides"
        return sum([len(liste_plateaux) for _, dico_nb_coups in self._ensemble_des_difficultes_de_plateaux.items() for _, liste_plateaux in dico_nb_coups.items()])

    @property
    def est_deja_termine(self) -> bool:
        return self._recherche_terminee


    # API io
    def exporter_fichier_json(self) -> None:
        from .io import exporter_fichier_json
        exporter_fichier_json(self)

    def arret_des_enregistrements(self) -> None:
        from .io import arret_des_enregistrements
        arret_des_enregistrements(self)

    # def init_export_json(self) -> None:
    #     from .io import init_export_json
    #     init_export_json(self)

    # def importer_fichier_json(self) -> None:
    #     from .io import importer_fichier_json
    #     importer_fichier_json(self)

    def to_dict(self) -> dict:
        from .io import to_dict
        return to_dict(self)


    # API filter
    @property
    def est_filtre_plateaux_invalides_ou_ininteressants(self) -> bool:
        return self._filtrer_plateaux_invalides_ou_ininteressants

    @property
    def est_filtre_doublons_permutation_jetons(self) -> bool:
        return self._filtrer_doublons_permutation_jetons

    @property
    def est_filtre_doublons_permutation_piles(self) -> bool:
        return self._filtrer_doublons_permutation_piles

    @property
    def est_filtre_doublons_permutation_jetons_piles(self) -> bool:
        return self._filtrer_doublons_permutation_jetons_piles

    def filtrer_plateaux_invalides_ou_initeressants(self, periode_affichage) -> None:
        from .filter import filtrer_plateaux_invalides_ou_ininteressants
        filtrer_plateaux_invalides_ou_ininteressants(self, periode_affichage)

    def filtrer_doublons_permutation_jetons(self, periode_affichage) -> None:
        from .filter import filtrer_doublons_permutation_jetons
        filtrer_doublons_permutation_jetons(self, periode_affichage)

    def filtrer_doublons_permutation_piles(self, periode_affichage) -> None:
        from .filter import filtrer_doublons_permutation_piles
        filtrer_doublons_permutation_piles(self, periode_affichage)

    def filtrer_doublons_permutation_jetons_piles(self, periode_affichage) -> None:
        from .filter import filtrer_doublons_permutation_jetons_piles
        filtrer_doublons_permutation_jetons_piles(self, periode_affichage)


    # API generator
    def creer_plateau_initial_optimisation_permutation(self) -> list:
        from .generator import creer_plateau_initial_optimisation_permutation
        return creer_plateau_initial_optimisation_permutation(self)

    def construire_les_permutations_de_colonnes(self, plateau: Plateau) -> list:
        from .generator import construire_les_permutations_de_colonnes
        return construire_les_permutations_de_colonnes(self, plateau)

    def construire_les_permutations_de_jetons(self, plateau: Plateau) -> list:
        from .generator import construire_les_permutations_de_jetons
        return construire_les_permutations_de_jetons(self, plateau)


    # API level
    def est_deja_connu_difficulte_plateau(self, plateau: Plateau) -> bool:
        from .level import est_deja_connu_difficulte_plateau
        return est_deja_connu_difficulte_plateau(self, plateau)

    def definir_difficulte_plateau(self, plateau: Plateau, difficulte, nb_coups) -> None:
        from .level import definir_difficulte_plateau
        definir_difficulte_plateau(self, plateau, difficulte, nb_coups)

    def effacer_difficulte_plateau(self) -> None:
        from .level import effacer_difficulte_plateau
        effacer_difficulte_plateau(self)

    def arret_des_enregistrements_de_difficultes_plateaux(self) -> None:
        from .level import arret_des_enregistrements_de_difficultes_plateaux
        arret_des_enregistrements_de_difficultes_plateaux(self)
