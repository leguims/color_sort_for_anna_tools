"""
Conversions entre formats :
- ligne brute
- ligne texte
- ligne texte universel (séparateur '.')
- rectangle
- rectangle texte
"""
from .model import Plateau

def creer_plateau_ligne_texte(plateau: Plateau) -> None:
    """['A', 'A', 'B', 'B', ' ', ' '] => ['AABB  ']"""
    if plateau.plateau_ligne:
        plateau.plateau_ligne_texte = ''.join(plateau.plateau_ligne)

def creer_plateau_ligne_texte_universel(plateau: Plateau) -> None:
    """['A', 'A', 'B', 'B', ' ', ' '] => ['AA.BB.  ']"""
    if not plateau.plateau_rectangle_texte:
        creer_plateau_rectangle_texte(plateau)
    if plateau.plateau_rectangle_texte:
        plateau.plateau_ligne_texte_universel = '.'.join(plateau.plateau_rectangle_texte)

def creer_plateau_rectangle(plateau: Plateau) -> None:
    """"['A', 'A', 'B', 'B', ' ', ' '] => [['A', 'A'], ['B', 'B'], [' ', ' ']]"""
    if plateau.plateau_ligne:
        plateau.plateau_rectangle = []
        for colonne in range(plateau.nb_colonnes):
            plateau.plateau_rectangle.append(
                plateau.plateau_ligne[colonne*plateau.nb_lignes : (colonne + 1)*plateau.nb_lignes])

def creer_plateau_rectangle_texte(plateau: Plateau) -> None:
    """"['A', 'A', 'B', 'B', ' ', ' '] => ['AA', 'BB', '  ']"""
    if plateau.plateau_ligne:
        plateau.plateau_rectangle_texte = []
        for colonne in range(plateau.nb_colonnes):
            plateau.plateau_rectangle_texte.append(''.join(
                plateau.plateau_ligne[colonne*plateau.nb_lignes : (colonne + 1)*plateau.nb_lignes]))

def creer_les_familles(plateau: Plateau) -> None:
    "Creer une liste des familles"
    if not plateau._liste_familles:
        plateau._liste_familles = [chr(ord('A')+F) for F in range(plateau._nb_familles) ]
