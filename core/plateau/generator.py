from .model import Plateau

def creer_plateau_initial(plateau: Plateau) -> None:
    """"Cree un plateau en ligne initial = ['A', 'A', 'B', 'B', ' ', ' ']"""
    if not plateau.plateau_ligne:
        plateau.plateau_ligne = tuple(
            [plateau.liste_familles[famille] for famille in range(plateau.nb_familles)
                                                for membre in range(plateau.nb_lignes)]
            +[plateau.case_vide for vide in range(plateau.nb_colonnes_vides)
                        for membre in range(plateau.nb_lignes)] )

def creer_plateau_permutation_initial(plateau: Plateau) -> None:
    """"Cree un plateau en ligne initial pour la permutation.
    Ce plateau est le premier plateau valide produit à partir
    du plateau retourné par le methode 'creer_plateau_initial'.
    exemple 4x4 = ['A', 'A', 'A', 'B', 'A', 'B', 'B', 'B', 'C', 'C', 'C', ' ', 'C', ' ', ' ', ' ']
    ... ='AAAB.ABBB.CCC .C   '"""
    # 2x7 : ['A'x(L-1)] .A[' 'x(L-1)]]
    # 3x7 : ['A'x(L-1)]B.A['B'x(L-1)].[' 'x(L)]]
    # 4x7 : ['A'x(L-1)]B.A['B'x(L-1)].['C'x(L-1)] .C[' 'x(L-1)]]
    # 5x7 : ['A'x(L-1)]B.A['B'x(L-1)].['C'x(L-1)]D.C['D'x(L-1)].[' 'x(L)]]
    # 6x7 : ['A'x(L-1)]B.A['B'x(L-1)].['C'x(L-1)]D.C['D'x(L-1)].['E'x(L-1)] .E[' 'x(L-1)]
    if not plateau.plateau_ligne:
        plateau_permutation = []
        famille_et_vide = plateau.liste_familles + [plateau.case_vide]
        for colonne in range(1, plateau.nb_colonnes+1):
            if colonne >= 2:
                famille_precedente = famille_et_vide[colonne-2]
            famille = famille_et_vide[colonne-1]
            if colonne < plateau.nb_colonnes:
                famille_suivante = famille_et_vide[colonne]

            if (colonne == plateau.nb_colonnes):
                # Derniere colonne (famille = plateau.case_vide)
                if plateau.nb_colonnes%2 == 0: # paire
                    plateau_permutation += [famille_precedente] + [famille]*(plateau.nb_lignes-1)
                else: # impaire
                    plateau_permutation += [famille]*plateau.nb_lignes
            else :
                if colonne%2 == 1: # impaire
                    plateau_permutation += [famille]*(plateau.nb_lignes-1) + [famille_suivante]
                else: # paire
                    plateau_permutation += [famille_precedente] + [famille]*(plateau.nb_lignes-1)
        plateau.plateau_ligne = tuple(plateau_permutation)
        plateau._logger.info(f"Plateau de permutation initial = '{plateau.plateau_ligne_texte_universel}'")
