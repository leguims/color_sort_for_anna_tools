"Module pour creer, resoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations
import datetime
import logging

from core.plateau import Plateau
from io_utils.export_json import ExportJSON

DELAI_ENREGISTRER_LOT_DE_PLATEAUX = 30*60
TAILLE_ENREGISTRER_LOT_DE_PLATEAUX = 100_000
DELAI_AFFICHER_ITER_LOT_DE_PLATEAUX = 5*60

# TODO : reprendre l'enregistrement a partir du fichier. => Pas d'amelioration, essayer de comprendre.

class LotDePlateaux:
    """Classe qui gere les lots de plateaux pour parcourir l'immensite des plateaux existants.
Le chanmps nb_plateaux_max designe la memoire allouee pour optimiser la recherche."""
    def __init__(self, dim_plateau, repertoire_export_json, nb_plateaux_max = 1_000_000):
        # Plateau de base
        self._plateau_courant = Plateau(dim_plateau[0], dim_plateau[1], dim_plateau[2])

        # Gestion du lot de plateau
        self._ensemble_des_plateaux_valides = set() # Plateaux valides collectés dans la recherche.
        self._ensemble_des_plateaux_a_ignorer = set() # Plateaux invalides collectés dans la recherche.
        self._ensemble_des_permutations_de_nombres = None # Ensemble constant utilisé pour les permutations de jetons
        self._iter_index = 0  # Initialisation de l'index de l'itérateur
        self._nb_plateaux_max = nb_plateaux_max # Limite memoire pour la recherche (plateaux à ignorer)
        self._export_json = None
        self._ensemble_des_difficultes_de_plateaux = {} # Ensemble des plateaux classés par difficulté et profondeur
        self._a_change = False # Indique si les données de la classe ont changé.
        self._logger = logging.getLogger(f"{self._plateau_courant.nb_colonnes}.{self._plateau_courant.nb_lignes}.{LotDePlateaux.__name__}")
        self._recherche_terminee = False # Indique si la recherche de plateaux valides est terminee (exhaustive)
        self._recherche_dernier_plateau = None # Dernier plateau traité en recherche pour reprise
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
            self._iter_permutation_optimisee = self.creer_plateau_initial_optimisation_permutation()
            # Initialisation : commencer les permutations avec le dernier plateau valide
            self._iter_iterateur = permutations(self._iter_permutation_optimisee)
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
            dernier_affichage  = datetime.datetime.now().timestamp() - DELAI_AFFICHER_ITER_LOT_DE_PLATEAUX
            derniere_iter = []
            while True:
                # Itérer avec les permutations
                self._iter_permutation = next(self._iter_iterateur)
                if derniere_iter == self._iter_permutation:
                    continue
                derniere_iter = self._iter_permutation
                # Ultime optimisation :
                #  - Si la colonne 1 n'a pas de 'A' => FIN des permutations.
                nb_A_sur_colonne_1 = self._iter_permutation[0:self._plateau_courant.nb_lignes].count('A')
                if nb_A_sur_colonne_1 == 0:
                    break
                # Astuce d'optimisation : ignorer la permutation ...
                #  - Si la colonne 1 est remplie de 'A'.
                if nb_A_sur_colonne_1 == self._plateau_courant.nb_lignes:
                    continue
                # Astuce identique avec la dernière colonne et la case vide ' '
                #  - Si la colonne N n'a pas de ' '.
                nb_VIDE_sur_colonne_N = self._iter_permutation[-self._plateau_courant.nb_lignes:].count(' ')
                if nb_VIDE_sur_colonne_N == 0:
                    continue
                est_ignore = self.plateau_est_ignore(''.join(self._iter_permutation))
                if est_ignore and not self._plateau_courant.est_valide:
                    self._plateau_courant.rendre_valide()
                    # 'self.est_ignore' ajusté
                    if self._plateau_courant.est_interessant:
                        self.ajouter_le_plateau(self._plateau_courant)
                        est_ignore = False
                        # Ne pas poursuivre l'itération à ce plateau valide
                    else:
                        self.ignorer_le_plateau(self._plateau_courant)

                # Enregistrement du plateau courant pour une eventuelle reprise.
                self._recherche_dernier_plateau = self._plateau_courant.plateau_ligne_texte_universel
                self._export_json.exporter(self)
                # Log pour suivre l'avancement.
                if datetime.datetime.now().timestamp() - dernier_affichage > DELAI_AFFICHER_ITER_LOT_DE_PLATEAUX:
                    self.logger.info(f"self._recherche_dernier_plateau='{self._recherche_dernier_plateau}'")
                    dernier_affichage  = datetime.datetime.now().timestamp()
                if est_ignore:
                    self.logger.debug(f"__next__ : Plateau ignore. '{self._plateau_courant.plateau_ligne_texte_universel}'")
                else:
                    # Retourner le plateau valide
                    self.logger.debug(f"__next__ : Plateau valide. '{self._plateau_courant.plateau_ligne_texte_universel}'")
                    return self._plateau_courant.plateau_ligne_texte_universel
        self.arret_des_enregistrements()
        raise StopIteration

    def __len__(self) -> int:
        return self.nb_plateaux_valides

    @property
    def logger(self) -> set:
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
    def nb_plateaux_ignores(self) -> int:
        "Nombre de plateaux ignores"
        return len(self._ensemble_des_plateaux_a_ignorer)

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
    def plateau_est_ignore(self, permutation_plateau) -> bool:
        from .filter import plateau_est_ignore
        return plateau_est_ignore(self, permutation_plateau)

    def ajouter_le_plateau(self, plateau: Plateau) -> None:
        from .filter import ajouter_le_plateau
        ajouter_le_plateau(self, plateau)

    def ignorer_le_plateau(self, plateau_a_ignorer: Plateau) -> None:
        from .filter import ignorer_le_plateau
        ignorer_le_plateau(self, plateau_a_ignorer)

    def fixer_taille_memoire_max(self, nb_plateaux_max) -> None:
        from .filter import fixer_taille_memoire_max
        fixer_taille_memoire_max(self, nb_plateaux_max)

    def reduire_memoire(self) -> None:
        from .filter import reduire_memoire
        reduire_memoire(self)

    def effacer_plateaux_valides(self, set_plateaux_a_effacer, prefixe_log, plateau_courant) -> None:
        from .filter import effacer_plateaux_valides
        effacer_plateaux_valides(self, set_plateaux_a_effacer, prefixe_log, plateau_courant)

    def filtrer_totalement(self, periode_affichage) -> None:
        from .filter import filtrer_totalement
        filtrer_totalement(self, periode_affichage)

    @property
    def est_filtre_plateaux_invalides_ou_initeressants(self) -> bool:
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
        from .filter import filtrer_plateaux_invalides_ou_initeressants
        filtrer_plateaux_invalides_ou_initeressants(self, periode_affichage)

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
