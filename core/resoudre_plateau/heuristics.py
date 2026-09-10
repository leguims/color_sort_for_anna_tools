from .model import ResoudrePlateau

def difficulte_classique(resoudre_plateau: ResoudrePlateau) -> int:
    """Retourne la difficulte de la solution du gameplay CLASSIQUE
    La difficulté, c'est le rapport:
    - Le nombre de blocages
    - Le nombre de solutions"""
    if resoudre_plateau._solution is None:
        return 0
    # -1 : Remettre à jour ; 0 : remettre à jour par précaution
    if resoudre_plateau._difficulte_classique <= 0:
        nb_solutions = sum(resoudre_plateau._dico_des_longueurs_de_solutions.values())
        nb_blocages = sum(resoudre_plateau._dico_des_longueurs_de_blocages.values())
        if nb_solutions + nb_blocages == 0:
            return 0
        resoudre_plateau._difficulte_classique = round( 100. * nb_blocages / (nb_blocages + nb_solutions) )
        # print(f"Calcul de la difficulté : {nb_blocages} / {nb_blocages + nb_solutions} = {resoudre_plateau._difficulte_classique}% pour le plateau '{resoudre_plateau._plateau_initial.plateau_ligne_texte_universel}' avec une solution de longueur {len(resoudre_plateau._solution)}")

        _enregistrer_difficulte(resoudre_plateau)
    return resoudre_plateau._difficulte_classique

def difficulte_qui_perd_gagne(resoudre_plateau: ResoudrePlateau) -> int:
    """Retourne la difficulte de la solution du gameplay QUI_PERD_GAGNE
    La difficulté, c'est le rapport:
    - Le nombre de solutions
    - Le nombre de blocages"""
    if resoudre_plateau._solution is None:
        return 0
    # -1 : Remettre à jour ; 0 : remettre à jour par précaution
    if resoudre_plateau._difficulte_qui_perd_gagne <= 0:
        nb_solutions = sum(resoudre_plateau._dico_des_longueurs_de_solutions.values())
        nb_blocages = sum(resoudre_plateau._dico_des_longueurs_de_blocages.values())
        if nb_solutions + nb_blocages == 0:
            return 0
        resoudre_plateau._difficulte_qui_perd_gagne = round( 100. * nb_solutions / (nb_blocages + nb_solutions) )
        # print(f"Calcul de la difficulté : {nb_solutions} / {nb_blocages + nb_solutions} = {resoudre_plateau._difficulte_qui_perd_gagne}% pour le plateau '{resoudre_plateau._plateau_initial.plateau_ligne_texte_universel}' avec une solution de longueur {len(resoudre_plateau._solution)}")

        _enregistrer_difficulte(resoudre_plateau)
    return resoudre_plateau._difficulte_qui_perd_gagne

def _enregistrer_difficulte(resoudre_plateau: ResoudrePlateau):
    # Rechercher terminée ...
    # ... Enregistrer la difficulté dans le fichier JSON
    if resoudre_plateau._recherche_terminee:
        resoudre_plateau._export_json_solutions.forcer_export(resoudre_plateau)
        print("Resolution" \
                + f" '{resoudre_plateau._plateau_initial.plateau_ligne_texte.replace(' ', '-')}'" \
                + " : MaJ difficulte")