"Analyse de la pertinence d'un plateau pour le tri de couleur"

from .model import Plateau
from .ops import une_colonne_est_pleine_et_monocouleur

def est_interessant(plateau: Plateau) -> bool:
    """"Verifie si le plateau en parametre est interessant"""
    if plateau.plateau_ligne and plateau._est_interessant is None:
        plateau._est_interessant = True
        # Est-ce que le plateau est interessant ?
        # Une colonne achevee est sans interet.
        plateau._est_interessant =  not une_colonne_est_pleine_et_monocouleur(plateau)
    return plateau._est_interessant
