from .model import Plateau


# Fonctions publiques

def la_colonne_est_vide(plateau: Plateau, colonne) -> bool:
    """Retourne True si la colonne est vide, False sinon."""
    if colonne >= plateau.nb_colonnes:
        raise IndexError(f"Le numero de colonne est hors du plateau ({colonne}>={plateau.nb_colonnes}).")
    return plateau.plateau_rectangle_texte[colonne].isspace()

def la_colonne_est_pleine(plateau: Plateau, colonne) -> bool:
    """Retourne True si la colonne est pleine, False sinon."""
    if colonne >= plateau.nb_colonnes:
        raise IndexError(f"Le numero de colonne est hors du plateau ({colonne}>={plateau.nb_colonnes}).")
    return plateau.plateau_rectangle_texte[colonne].count(plateau.case_vide) == 0

def la_colonne_est_pleine_et_monocouleur(plateau: Plateau, colonne) -> bool:
    """Retourne True si la colonne est pleine et monocouleur, False sinon."""
    est_pleine = plateau.la_colonne_est_pleine(colonne)
    colonne_texte = plateau.plateau_rectangle_texte[colonne]
    premiere_case = colonne_texte[0]
    return est_pleine and colonne_texte.count(premiere_case) == plateau.nb_lignes

def une_colonne_est_pleine_et_monocouleur(plateau: Plateau) -> bool:
    """Retourne True si au moins une colonne est pleine et monocouleur, False sinon."""
    for colonne in range(plateau.nb_colonnes):
        if la_colonne_est_pleine_et_monocouleur(plateau, colonne):
            return True
    return False

def la_couleur_au_sommet_de_la_colonne(plateau: Plateau, colonne) -> str:
    """Retourne la couleur de la premiere case non vide de la colonne, ou une case vide si la colonne est vide."""
    if colonne >= plateau.nb_colonnes:
        raise IndexError(f"Le numero de colonne est hors du plateau ({colonne}>={plateau.nb_colonnes}).")
    colonne_texte = plateau.plateau_rectangle_texte[colonne]
    derniere_case_non_vide = colonne_texte.strip()[-1]
    return derniere_case_non_vide

def nombre_de_case_vide_de_la_colonne(plateau: Plateau, colonne) -> int:
    """Retourne le nombre de cases vides de la colonne."""
    if colonne >= plateau.nb_colonnes:
        raise IndexError(f"Le numero de colonne est hors du plateau ({colonne}>={plateau.nb_colonnes}).")
    colonne_texte = plateau.plateau_rectangle_texte[colonne]
    return len(colonne_texte) - len(colonne_texte.rstrip())

def nombre_de_cases_monocouleur_au_sommet_de_la_colonne(plateau: Plateau, colonne) -> int:
    """Retourne le nombre de cases de la couleur au sommet de la colonne."""
    couleur = la_couleur_au_sommet_de_la_colonne(plateau, colonne)
    colonne_texte = plateau.plateau_rectangle_texte[colonne]
    return compter_la_couleur_au_sommet(colonne_texte, couleur)

def deplacer_blocs(plateau: Plateau, colonne_depart, colonne_arrivee, nombre_blocs = 1) -> None:
    # Vérification logique : le nombre de bloc a deplacer doit etre egal au nombre de cases monocouleur au sommet de la colonne de depart
    if nombre_blocs != plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(colonne_depart):
        raise ValueError("Le nombre de bloc a deplacer est different de celui du plateau")
    deplacer_blocs_sans_verification(plateau, colonne_depart, colonne_arrivee, nombre_blocs)

def annuler_le_deplacer_blocs(plateau: Plateau, colonne_depart_a_annuler, colonne_arrivee_a_annuler, nombre_blocs = 1) -> None:
    # Annuler n'est pas logique, il separe une suite de blocs monocouleurs
    deplacer_blocs_sans_verification(plateau, colonne_arrivee_a_annuler, colonne_depart_a_annuler, nombre_blocs)

# Fonctions internes

def compter_la_couleur_au_sommet(colonne_texte, couleur) -> int:
    """Compte le nombre de cases de la couleur au sommet de la colonne."""
    nb = 0
    colonne_inversee = list(colonne_texte.rstrip())
    colonne_inversee.reverse()
    for case in colonne_inversee:
        if case == couleur:
            nb += 1
        else:
            break
    return nb

def deplacer_blocs_sans_verification(plateau: Plateau, colonne_depart, colonne_arrivee, nombre_blocs = 1) -> None:
    # Vérification technique
    if nombre_blocs > plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(colonne_depart):
        raise ValueError("Le nombre de bloc a deplacer est superieur a celui du plateau")
    if nombre_blocs > plateau.nombre_de_case_vide_de_la_colonne(colonne_arrivee):
        raise ValueError("Le nombre de bloc a deplacer est plus grand que ce que la colonne peut recevoir")
    couleur = la_couleur_au_sommet_de_la_colonne(plateau, colonne_depart)

    # Modification du plateau
    plateau_a_modifier = plateau.plateau_rectangle_texte
    # Inverser la colonne pour remplacer les couleur du haut, puis retablir l'ordre
    # colonne de depart : 'ABAA' => 'AABA' => '  BA' => 'AB  '
    plateau_a_modifier[colonne_depart] = plateau_a_modifier[colonne_depart][::-1].replace(couleur, plateau.case_vide, nombre_blocs)[::-1]
    # colonne d'arrivee : 'C   ' => 'CAA '
    plateau_a_modifier[colonne_arrivee] = plateau_a_modifier[colonne_arrivee].replace(plateau.case_vide, couleur, nombre_blocs)

    # Apllication de la modification
    plateau.plateau_rectangle_texte = plateau_a_modifier
