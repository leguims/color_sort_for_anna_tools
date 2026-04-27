from .model import Plateau
from .ops import une_colonne_est_pleine_et_monocouleur

def plateau_est_valide(plateau: Plateau) -> bool:
    """"Verifie si le plateau en parametre est valide"""
    if plateau.plateau_ligne and plateau._est_valide is None:
        # Vérifier la validité du plateau
        # Pour chaque colonne, les cases vides sont sur les dernieres cases

        # Construction de la position des cases vides
        count = plateau.plateau_ligne.count(plateau.case_vide)
        index_vide = []
        index_courant = -1
        for _ in range(count):
            index_courant = plateau.plateau_ligne.index(plateau.case_vide, index_courant+1)
            index_vide.append(index_courant)
        index_vide = tuple(index_vide) # l'index_vide devient invariable
        
        # Est-ce que cet index est valide ?
        if index_vide in plateau._dico_validite_index_vide:
            return plateau._dico_validite_index_vide.get(index_vide)
        
        # Index inconnu, identifier sa validite
        for colonne in range(plateau.nb_colonnes):
            case_vide_presente = False
            for ligne in range(plateau.nb_lignes):
                if not case_vide_presente:
                    # Chercher la premiere case vide de la colonne
                    if (colonne * plateau.nb_lignes + ligne) in index_vide:
                        case_vide_presente = True
                else:
                    # Toutes les autres case de la lignes doivent etre vides
                    if (colonne * plateau.nb_lignes + ligne) not in index_vide:
                        plateau._est_valide = False
                        plateau._dico_validite_index_vide[index_vide] = plateau._est_valide
                        return plateau._est_valide
        plateau._est_valide = True
        plateau._dico_validite_index_vide[index_vide] = plateau._est_valide
    return plateau._est_valide

def plateau_est_interessant(plateau: Plateau) -> bool:
    """"Verifie si le plateau en parametre est interessant"""
    if plateau.plateau_ligne and plateau._est_interessant is None:
        plateau._est_interessant = True
        # Est-ce que le plateau est interessant ?
        # Une colonne achevee est sans interet.
        plateau._est_interessant =  not une_colonne_est_pleine_et_monocouleur(plateau)
    return plateau._est_interessant
