import copy

from .model import ResoudrePlateau
from core.plateau import Plateau
from .choix import ensemble_des_choix_possibles, ajouter_choix, retirer_choix
from .validation import choix_est_valide, le_plateau_est_gagnant
from .io import exporter_fichier_json

def enregistrer_solution(resoudre_plateau: ResoudrePlateau, liste_des_choix_courants) -> None:
    "Enregistre le parcours de la solution pour la restituer"
    len_solution_courante = len(liste_des_choix_courants)
    # Si elle est plus courte, enregistrer la liste des choix courant comme la solution
    if resoudre_plateau._solution is None or len_solution_courante < len(resoudre_plateau._solution):
        resoudre_plateau._solution = copy.deepcopy(liste_des_choix_courants)

    # Mettre a jour les statistiques
    if len_solution_courante in resoudre_plateau._dico_des_longueurs_de_solutions:
        resoudre_plateau._dico_des_longueurs_de_solutions[len_solution_courante] += 1
    else:
        resoudre_plateau._dico_des_longueurs_de_solutions[len_solution_courante] = 1

    resoudre_plateau._export_json_solutions.forcer_export(resoudre_plateau)

def enregistrer_blocage(resoudre_plateau: ResoudrePlateau, liste_des_choix_courants) -> None:
    "Enregistre le parcours du blocage pour le restituer"
    len_blocage_courant = len(liste_des_choix_courants)

    # Mettre a jour les statistiques
    if len_blocage_courant in resoudre_plateau._dico_des_longueurs_de_blocages:
        resoudre_plateau._dico_des_longueurs_de_blocages[len_blocage_courant] += 1
    else:
        resoudre_plateau._dico_des_longueurs_de_blocages[len_blocage_courant] = 1

    resoudre_plateau._export_json_solutions.forcer_export(resoudre_plateau)

def backtracking(resoudre_plateau: ResoudrePlateau, plateau: Plateau = None, liste_des_choix_courants = None, profondeur_recursion = None) -> None:
    "Parcours de tous les choix afin de debusquer toutes les solutions"
    if plateau is None:
        if resoudre_plateau._recherche_terminee:
            # Le plateau est deja resolu et enregistre
            print("Resolution" \
                    + f" '{resoudre_plateau._plateau_initial.plateau_ligne_texte.replace(' ', '-')}'" \
                    + " : deja resolu")
            return
        plateau = copy.deepcopy(resoudre_plateau._plateau_initial)
        liste_des_choix_courants = []
        profondeur_recursion = -1
    
    profondeur_recursion += 1
    if profondeur_recursion > 50:
        raise RuntimeError("Appels recursifs infinis !")
    
    if le_plateau_est_gagnant(resoudre_plateau, plateau):   # Condition d'arret
        enregistrer_solution(resoudre_plateau, liste_des_choix_courants)
        profondeur_recursion -= 1
        return

    blocage = True
    for choix in ensemble_des_choix_possibles(resoudre_plateau):
        if choix_est_valide(plateau, choix):  # Verifier si le choix est valide
            blocage = False
            # Enrichir le choix du nombre de cases a deplacer (pour pouvoir retablir)
            nb_cases_deplacees = plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(choix[0])
            choix += tuple([nb_cases_deplacees])
            ajouter_choix( plateau, liste_des_choix_courants, choix)  # Prendre ce choix
            backtracking(resoudre_plateau, plateau, liste_des_choix_courants, profondeur_recursion)  # Appeler recursivement la fonction
            retirer_choix(plateau, liste_des_choix_courants, choix)  # Annuler le choix (retour en arriere)

    if blocage:
        enregistrer_blocage(resoudre_plateau, liste_des_choix_courants)
    
    if profondeur_recursion == 0:
        # fin de toutes les recherches
        resoudre_plateau._recherche_terminee = True
        exporter_fichier_json(resoudre_plateau)
        print("Resolution" \
                + f" '{resoudre_plateau._plateau_initial.plateau_ligne_texte.replace(' ', '-')}'" \
                + " : resolution achevee")

    profondeur_recursion -= 1

