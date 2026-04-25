from .model import Plateau
from .exceptions import PlateauInvalidable

def rendre_valide(plateau: Plateau) -> None:
    if not plateau.est_valide:
        plateau_valide_ligne_texte = ''
        for ligne in plateau.plateau_rectangle:
            # Les cases vides sont sur les dernieres cases de la colonne
            ligne_valide_rectangle = sorted(ligne, key=lambda x: x == plateau.case_vide)
            ligne_valide_texte = ''.join(ligne_valide_rectangle)
            plateau_valide_ligne_texte += ligne_valide_texte
        plateau_valide = Plateau(plateau.nb_colonnes, plateau.nb_lignes, plateau.nb_colonnes_vides)
        plateau_valide.clear()
        plateau_valide.plateau_ligne_texte = plateau_valide_ligne_texte
        if plateau_valide.est_valide:
            plateau.clear()
            plateau.plateau_ligne = plateau_valide.plateau_ligne
            plateau._logger.debug(f"Plateau rendu valide = '{plateau.plateau_ligne_texte}'")
        else:
            plateau._logger.error(f"Le plateau rendu valide n'est pas valide : '{plateau_valide.plateau_ligne_texte}'")
            raise PlateauInvalidable("Le plateau rendu valide n'est pas valide")
