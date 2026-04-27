"Module pour creer, resoudre et qualifier les solutions des plateaux de 'ColorWoordSort'"
import logging

# TODO : reprendre l'enregistrement a partir du fichier. => Pas d'amelioration, essayer de comprendre.

class Plateau:
    "Classe qui implemente un plateau. Son contenu et ses differentes representations."
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides=1):
        self._case_vide = ' '
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._dico_validite_index_vide = {}
        self.clear()
        self._nb_familles = nb_colonnes - nb_colonnes_vides
        self._liste_familles = []
        self._logger = logging.getLogger(f"{self._nb_colonnes}.{self._nb_lignes}.{Plateau.__name__}")

    def clear(self) -> None:
        "Efface le plateau pour en ecrire un nouveau"
        self._est_valide = None
        self._est_interessant = None
        # plateau_ligne : ['A', 'A', 'B', 'B', ' ', ' ']
        self._plateau_ligne = None
        # plateau_ligne_texte : ['AABB  ']
        self._plateau_ligne_texte = None
        # plateau_ligne_texte_universel : ['AA.BB.  ']
        self._plateau_ligne_texte_universel = None
        # plateau_rectangle : [['A', 'A'], ['B', 'B]', [' ', ' ']]
        self._plateau_rectangle = None
        # plateau_rectangle_texte : ['AA', 'BB', '  ']
        self._plateau_rectangle_texte = None
        self._str_format = ""

    def __str__(self) -> str:
        if not self._str_format:
            for ligne in self.plateau_rectangle:
                self._str_format += f"{ligne}\n"
        return self._str_format

    def __eq__(self, autre) -> bool:
        if not isinstance(autre, Plateau):
            # Ne sont pas comparables
            return NotImplemented
        # Comparer taille et contenu
        return (self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides, self._plateau_ligne) == \
            (autre._nb_colonnes, autre._nb_lignes, autre._nb_colonnes_vides, autre._plateau_ligne)

    def __hash__(self):
        return hash((self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides, self._plateau_ligne))

    @property
    def case_vide(self) -> str:
        "Caractere pour une case vide"
        return self._case_vide

    @property
    def logger(self) -> str:
        "Logger pour le plateau"
        return self._logger

    @property
    def nb_colonnes(self) -> int:
        "Nombre de colonnes du plateau"
        return self._nb_colonnes

    @property
    def nb_lignes(self) -> int:
        "Nombre de lignes du plateau"
        return self._nb_lignes

    @property
    def nb_colonnes_vides(self) -> int:
        "Nombre de colonnes vides du plateau"
        return self._nb_colonnes_vides

    @property
    def plateau_ligne(self) -> tuple:
        """Representation en 1 ligne du plateau (liste)
        'AA.BB.  ' => ['A', 'A', 'B', 'B', ' ', ' ']"""
        return self._plateau_ligne

    @plateau_ligne.setter
    def plateau_ligne(self, plateau_ligne) -> None:
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self.clear()
        self._plateau_ligne = tuple(plateau_ligne)

    @property
    def plateau_ligne_texte(self) -> str:
        """Representation en 1 ligne du plateau (texte)
        'AA.BB.  ' => 'AABB  '"""
        if not self._plateau_ligne_texte:
            from .format import  creer_plateau_ligne_texte
            creer_plateau_ligne_texte(self)
        return self._plateau_ligne_texte

    @plateau_ligne_texte.setter
    def plateau_ligne_texte(self, plateau_ligne_texte) -> None:
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self.plateau_ligne = [c for c in plateau_ligne_texte] # via setter
        self._plateau_ligne_texte = plateau_ligne_texte

    @property
    def plateau_ligne_texte_universel(self) -> str:
        """Representation en 1 ligne du plateau (texte)
        'AA.BB.  ' => 'AA.BB.  '"""
        if not self._plateau_ligne_texte_universel:
            from .format import creer_plateau_ligne_texte_universel
            creer_plateau_ligne_texte_universel(self)
        return self._plateau_ligne_texte_universel

    @plateau_ligne_texte_universel.setter
    def plateau_ligne_texte_universel(self, plateau_ligne_texte_universel) -> None:
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self._plateau_ligne_texte = plateau_ligne_texte_universel.replace('.', '')
        self.plateau_ligne = [c for c in self._plateau_ligne_texte] # via setter

    @property
    def plateau_rectangle(self) -> list:
        """Representation en rectangle (colonnes et lignes) du plateau (liste)
        'AA.BB.  ' => [['A', 'A'], ['B', 'B'], [' ', ' ']]"""
        if not self._plateau_rectangle:
            from .format import creer_plateau_rectangle
            creer_plateau_rectangle(self)
        return self._plateau_rectangle

    @property
    def plateau_rectangle_texte(self) -> list:
        """Representation en rectangle (colonnes et lignes) du plateau (texte)
        'AA.BB.  ' => ['AA', 'BB', '  ']"""
        if not self._plateau_rectangle_texte:
            from .format import creer_plateau_rectangle_texte
            creer_plateau_rectangle_texte(self)
        return self._plateau_rectangle_texte

    @plateau_rectangle_texte.setter
    def plateau_rectangle_texte(self, plateau_rectangle_texte) -> None:
        # Rectangle_texte => plateau_ligne_texte
        plateau_ligne_texte = ''.join(plateau_rectangle_texte)
        # plateau_ligne_texte => plateau_ligne
        self.plateau_ligne = [c for c in plateau_ligne_texte]

    @property
    def pour_permutations(self) -> tuple:
        "Format du plateau utilise pour les permutations"
        return self.plateau_ligne

    @property
    def nb_familles(self) -> int:
        "Nombre de familles de couleurs dans le plateau"
        return self._nb_familles

    @property
    def liste_familles(self) -> list:
        """Liste des familles de couleurs dans le plateau"""
        if not self._liste_familles:
            from .format import creer_les_familles
            creer_les_familles(self)
        return self._liste_familles

    @property
    def pour_permutations(self) -> tuple:
        "Format du plateau utilise pour les permutations"
        return self.plateau_ligne


    # API Ops
    def la_colonne_est_vide(self, colonne) -> bool:
        from .ops import la_colonne_est_vide
        return la_colonne_est_vide(self, colonne)

    def la_colonne_est_pleine(self, colonne) -> bool:
        from .ops import la_colonne_est_pleine
        return la_colonne_est_pleine(self, colonne)

    def la_colonne_est_pleine_et_monocouleur(self, colonne) -> bool:
        from .ops import la_colonne_est_pleine_et_monocouleur
        return la_colonne_est_pleine_et_monocouleur(self, colonne)

    def une_colonne_est_pleine_et_monocouleur(self) -> bool:
        from .ops import une_colonne_est_pleine_et_monocouleur
        return une_colonne_est_pleine_et_monocouleur(self)

    def la_couleur_au_sommet_de_la_colonne(self, colonne) -> str:
        from .ops import la_couleur_au_sommet_de_la_colonne
        return la_couleur_au_sommet_de_la_colonne(self, colonne)

    def nombre_de_case_vide_de_la_colonne(self, colonne) -> int:
        from .ops import nombre_de_case_vide_de_la_colonne
        return nombre_de_case_vide_de_la_colonne(self, colonne)

    def nombre_de_cases_monocouleur_au_sommet_de_la_colonne(self, colonne) -> int:
        from .ops import nombre_de_cases_monocouleur_au_sommet_de_la_colonne
        return nombre_de_cases_monocouleur_au_sommet_de_la_colonne(self, colonne)

    def deplacer_blocs(self, colonne_depart, colonne_arrivee, nombre_blocs = 1) -> None:
        from .ops import deplacer_blocs
        deplacer_blocs(self, colonne_depart, colonne_arrivee, nombre_blocs)

    def annuler_le_deplacer_blocs(self, colonne_depart_a_annuler, colonne_arrivee_a_annuler, nombre_blocs = 1) -> None:
        from .ops import annuler_le_deplacer_blocs
        annuler_le_deplacer_blocs(self, colonne_depart_a_annuler, colonne_arrivee_a_annuler, nombre_blocs)

    # API Generator
    def creer_plateau_initial(self) -> None:
        from .generator import creer_plateau_initial
        creer_plateau_initial(self)
 
    def creer_plateau_permutation_initial(self) -> None:
        from .generator import creer_plateau_permutation_initial
        creer_plateau_permutation_initial(self)

    # API Normalize
    def rendre_valide(self) -> None:
        from .normalize import rendre_valide
        rendre_valide(self)

    # API Validator
    @property
    def est_valide(self) -> bool:
        from .validator import plateau_est_valide
        return plateau_est_valide(self)

    @property
    def est_interessant(self) -> bool:
        """"Verifie si le plateau en parametre est interessant"""
        from .validator import plateau_est_interessant
        return plateau_est_interessant(self)
