from .model import Plateau
from .exceptions import PlateauInvalidable
from .ops import (
    la_colonne_est_vide,
    la_colonne_est_pleine,
    la_colonne_est_pleine_et_monocouleur,
    une_colonne_est_pleine_et_monocouleur,
    la_couleur_au_sommet_de_la_colonne,
    nombre_de_case_vide_de_la_colonne,
    nombre_de_cases_monocouleur_au_sommet_de_la_colonne,
    deplacer_blocs
)
from .validator import est_valide
from .heuristics import est_interessant
from .normalize import rendre_valide
