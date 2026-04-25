import copy

from .model import ResoudrePlateau
from .choix import ensemble_des_choix_possibles, ajouter_choix
from .validation import est_valide

def difficulte(resoudre_plateau: ResoudrePlateau) -> int | None:
    """Retourne la difficulte de la solution
    La difficulté dépend de :
    - Le nombre de choix
    - La taille du plateau"""
    # TODO : Pour les tableaux 10x4, la valeur de difficulté explose.
    #        La division par (12x12 / 10x4) est à revoir.
    if resoudre_plateau._solution is None:
        return None
    if not resoudre_plateau._difficulte:
        surface_plateau_max = 12 * 12
        surface_plateau = resoudre_plateau._plateau_initial.nb_colonnes * resoudre_plateau._plateau_initial.nb_lignes
        inverse_ratio_surface = surface_plateau_max / surface_plateau

        # Parcourir la solution et quantifier le nombre de choix
        nb_choix_total = 1
        plateau = copy.deepcopy(resoudre_plateau._plateau_initial)
        liste_des_choix_courants = []
        for coup in resoudre_plateau._solution:
            nb_choix_courant = 0
            for choix_possible in ensemble_des_choix_possibles(resoudre_plateau):
                if est_valide(plateau, choix_possible):
                    nb_choix_courant += 1
            # Multiplier les niveaux de choix
            nb_choix_total *= nb_choix_courant
            # Appliquer le coup pour avancer dans la solution
            nb_cases_deplacees = plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(coup[0])
            coup += tuple([nb_cases_deplacees])
            ajouter_choix(plateau, liste_des_choix_courants, coup)  # Jouer ce coup

        resoudre_plateau._difficulte = int( nb_choix_total * inverse_ratio_surface )
        # print(f"Calcul de la difficulté : {nb_choix_total} x {inverse_ratio_surface} = {resoudre_plateau._difficulte} pour le plateau '{resoudre_plateau._plateau_initial.plateau_ligne_texte_universel.replace(' ','-')}' avec une solution de longueur {len(resoudre_plateau._solution)} (surface {surface_plateau})")

        # Rechercher terminée et il manque la difficulté ...
        # ... Enregistrer la difficulté dans le fichier JSON
        if resoudre_plateau._recherche_terminee:
            resoudre_plateau._export_json_solutions.forcer_export(resoudre_plateau)
            print("Resolution" \
                    + f" '{resoudre_plateau._plateau_initial.plateau_ligne_texte.replace(' ', '-')}'" \
                    + " : MaJ difficulte")
    return resoudre_plateau._difficulte

