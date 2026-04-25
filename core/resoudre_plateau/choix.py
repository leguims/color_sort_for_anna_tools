from .model import ResoudrePlateau
from core.plateau import Plateau

def ensemble_des_choix_possibles(resoudre_plateau: ResoudrePlateau) -> list:
    "Liste tous les choix possible pour un plateau (valide et invalides)"
    if not resoudre_plateau._liste_des_choix_possibles:
        # Liste de tous les possibles a construire selon la dimension du plateau
        resoudre_plateau._liste_des_choix_possibles = []
        for depart in range(resoudre_plateau._plateau_initial.nb_colonnes):
            for arrivee in range(resoudre_plateau._plateau_initial.nb_colonnes):
                if depart != arrivee:
                    resoudre_plateau._liste_des_choix_possibles.append(tuple([depart, arrivee]))
    # Nombre de choix = (nb_colonnes * (nb_colonnes-1))
    return resoudre_plateau._liste_des_choix_possibles

def ajouter_choix(plateau: Plateau, liste_des_choix_courants, choix) -> None:
    "Enregistre un choix et modifie le plateau selon ce choix"
    # Enregistrer le choix
    liste_des_choix_courants.append(choix[0:2])
    # Modifier le plateau
    plateau.deplacer_blocs(*choix)

def retirer_choix(plateau: Plateau, liste_des_choix_courants, choix) -> None:
    "Annule le dernier choix et restaure le plateau precedent"
    # Desenregistrer le choix
    liste_des_choix_courants.pop()
    # Modifier le plateau
    plateau.annuler_le_deplacer_blocs(*choix)
