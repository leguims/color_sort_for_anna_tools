from itertools import permutations

from .model import ResoudrePlateau
from core.plateau import Plateau

def est_valide(plateau: Plateau, choix) -> bool:
    "Verifie la validite du choix"
    c_depart, c_arrivee = choix
    # INVALIDE Si les colonnes de depart et d'arrivee sont identiques
    if c_depart == c_arrivee:
        return False
    # INVALIDE Si la colonne de depart est vide
    if plateau.la_colonne_est_vide(c_depart):
        return False
    # INVALIDE Si la colonne de depart est pleine et monocouleur
    if plateau.la_colonne_est_pleine_et_monocouleur(c_depart):
        return False
    # INVALIDE Si la colonne d'arrivee est pleine
    if plateau.la_colonne_est_pleine(c_arrivee):
        return False
    # INVALIDE Si la colonne d'arrivee n'est pas vide et n'a pas la meme couleur au sommet
    if not plateau.la_colonne_est_vide(c_arrivee) and \
        plateau.la_couleur_au_sommet_de_la_colonne(c_depart) != plateau.la_couleur_au_sommet_de_la_colonne(c_arrivee):
        return False
    # INVALIDE Si la colonne d'arrivee n'a pas assez de place
    if plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(c_depart) > plateau.nombre_de_case_vide_de_la_colonne(c_arrivee):
        return False
    return True

def ensemble_des_plateaux_gagnants(resoudre_plateau: ResoudrePlateau) -> list:
    "Liste tous les plateaux gagnants"
    if resoudre_plateau._liste_plateaux_gagnants is None:
        nb_c = resoudre_plateau._plateau_initial.nb_colonnes
        nb_l = resoudre_plateau._plateau_initial.nb_lignes
        nb_cv = resoudre_plateau._plateau_initial.nb_colonnes_vides
        plateau_gagnant = Plateau(nb_c, nb_l, nb_cv)
        plateau_gagnant.creer_plateau_initial()

        resoudre_plateau._liste_plateaux_gagnants = []
        # 'set()' est utilise pour eliminer les permutations identiques
        for permutation_courante in set(permutations(plateau_gagnant.plateau_rectangle_texte)):
            plateau_gagnant_courant = Plateau(nb_c, nb_l, nb_cv)
            plateau_gagnant_courant.plateau_rectangle_texte = permutation_courante
            resoudre_plateau._liste_plateaux_gagnants.append(plateau_gagnant_courant.plateau_ligne_texte)
    return resoudre_plateau._liste_plateaux_gagnants

def solution_complete(resoudre_plateau: ResoudrePlateau, plateau: Plateau) -> bool:
    "Evalue si le plateau est termine (gagne ou bloque)"
    if plateau.plateau_ligne_texte in resoudre_plateau.ensemble_des_plateaux_gagnants():
        return True
    # TODO : Evaluer si le plateau est "bloque" => a observer, mais verification inutile jusque la.
    return False

