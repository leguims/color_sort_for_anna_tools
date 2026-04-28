import copy

from .model import ResoudrePlateau
from .choix import ensemble_des_choix_possibles, ajouter_choix
from .validation import choix_est_valide

def difficulte(resoudre_plateau: ResoudrePlateau) -> int | None:
    """Retourne la difficulte de la solution
    La difficulté, c'est le rapport:
    - Le nombre de blocages
    - Le nombre de solutions"""
    if resoudre_plateau._solution is None:
        return None
    if not resoudre_plateau._difficulte:
        nb_solutions = sum(resoudre_plateau._dico_des_longueurs_de_solutions.values())
        nb_blocages = sum(resoudre_plateau._dico_des_longueurs_de_blocages.values())
        if nb_solutions + nb_blocages == 0:
            return None
        resoudre_plateau._difficulte = int( 100. * nb_blocages / (nb_blocages + nb_solutions) )
        # print(f"Calcul de la difficulté : {nb_blocages} / {nb_blocages + nb_solutions} = {resoudre_plateau._difficulte}% pour le plateau '{resoudre_plateau._plateau_initial.plateau_ligne_texte_universel}' avec une solution de longueur {len(resoudre_plateau._solution)}")

        # Rechercher terminée et il manque la difficulté ...
        # ... Enregistrer la difficulté dans le fichier JSON
        if resoudre_plateau._recherche_terminee:
            resoudre_plateau._export_json_solutions.forcer_export(resoudre_plateau)
            print("Resolution" \
                    + f" '{resoudre_plateau._plateau_initial.plateau_ligne_texte.replace(' ', '-')}'" \
                    + " : MaJ difficulte")
    return resoudre_plateau._difficulte

