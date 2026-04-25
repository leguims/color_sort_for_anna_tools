from itertools import permutations

from .model import LotDePlateaux
from core.plateau import Plateau

def creer_plateau_initial_optimisation_permutation(lot_de_plateaux: LotDePlateaux) -> list:
    """"Reprendre au plateau valide le plus avancé dans les permutations
    ou créer le plateau de permutations initial."""
    if lot_de_plateaux._recherche_dernier_plateau is not None:
        lot_de_plateaux._logger.info("Recherche : Reprendre au dernier plateau")
        lot_de_plateaux._plateau_courant.clear()
        lot_de_plateaux._plateau_courant.plateau_ligne_texte_universel = lot_de_plateaux._recherche_dernier_plateau
        return lot_de_plateaux._plateau_courant.pour_permutations

    # TODO : Vérifier que ce code est obsolète
    #if lot_de_plateaux.plateaux_valides:
    #    # Reprendre au premier plateau valide classé (c'est le plus avancé dans les permutations)
    #    # 'A   ' est plus loin que 'AAA ' dans les permutations
    #    return [i for i in lot_de_plateaux.plateaux_valides_liste_classee[0]]

    # Sinon, calculer le plateau initial de permutations
    lot_de_plateaux._plateau_courant.creer_plateau_permutation_initial()
    return lot_de_plateaux._plateau_courant.pour_permutations

def construire_les_permutations_de_colonnes(lot_de_plateaux: LotDePlateaux, plateau: Plateau) -> list:
    """Methode qui construit les permutations de colonnes d'un plateau.
Le plateau lui-meme n'est pas dans les permutations."""
    liste_permutations_de_colonnes = []
    # 'set()' est utilise pour eliminer les permutations identiques
    for permutation_courante in set(permutations(plateau.plateau_rectangle_texte)):
        plateau_a_ignorer = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
        plateau_a_ignorer.plateau_rectangle_texte = permutation_courante

        # Ignorer toutes les permutations
        if plateau_a_ignorer.plateau_ligne_texte != plateau.plateau_ligne_texte:
            liste_permutations_de_colonnes.append(plateau_a_ignorer)
    return liste_permutations_de_colonnes

def construire_les_permutations_de_jetons(lot_de_plateaux: LotDePlateaux, plateau: Plateau) -> list:
    """Methode qui construit les permutations de jetons d'un plateau.
Par exemple, ces deux plateaux sont equivalents pour un humain : 'ABC.CBA' ==(A devient B)== 'BAC.CAB'
Le plateau lui-meme n'est pas dans les permutations."""
    # Liste des permutations 'nombre'
    if lot_de_plateaux._ensemble_des_permutations_de_nombres is None:
        lot_de_plateaux._ensemble_des_permutations_de_nombres = set(permutations(range(lot_de_plateaux._plateau_courant.nb_familles)))

    case_vide = ' '
    liste_permutations_de_jetons = []
    for permutation_nombre_courante in lot_de_plateaux._ensemble_des_permutations_de_nombres:
        # Pour chaque permutation, transposer le plateau
        permutation_jeton_courante = []
        for jeton in plateau.plateau_ligne:
            if jeton != case_vide:
                # Pour chaque jeton (sauf case vide), appliquer sa transposition
                indice_jeton = ord(jeton) - ord(lot_de_plateaux._plateau_courant.liste_familles[0])
                nouvel_indice_jeton = permutation_nombre_courante[indice_jeton]
                nouveau_jeton = lot_de_plateaux._plateau_courant.liste_familles[nouvel_indice_jeton]
            else:
                nouveau_jeton = case_vide
            # Creation de la transposition jeton apres jeton
            permutation_jeton_courante.append(nouveau_jeton)
        # Le plateau transpose est le plateau a ingorer
        plateau_a_ignorer = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
        plateau_a_ignorer.plateau_ligne = permutation_jeton_courante
        if plateau_a_ignorer.plateau_ligne_texte != plateau.plateau_ligne_texte:
            liste_permutations_de_jetons.append(plateau_a_ignorer)
    return liste_permutations_de_jetons

