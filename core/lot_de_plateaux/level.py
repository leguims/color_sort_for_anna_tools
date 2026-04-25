import copy

from .model import LotDePlateaux
from core.plateau import Plateau

def est_deja_connu_difficulte_plateau(lot_de_plateaux: LotDePlateaux, plateau: Plateau) -> bool:
    "Methode qui verifie si le plateau est deja resolu"
    est_connu = False
    for difficulte in lot_de_plateaux._ensemble_des_difficultes_de_plateaux.keys():
        if plateau.plateau_ligne_texte in lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte]:
            est_connu = True
            break
    return est_connu

def definir_difficulte_plateau(lot_de_plateaux: LotDePlateaux, plateau: Plateau, difficulte, nb_coups) -> None:
    "Methode qui enregistre les difficultes des plateaux et la profondeur de leur solution"
    if difficulte not in lot_de_plateaux._ensemble_des_difficultes_de_plateaux:
        lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte] = {}
    if nb_coups not in lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte]:
        lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups] = []
    if plateau.plateau_ligne_texte not in lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups]:
        lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups].append(plateau.plateau_ligne_texte)
        lot_de_plateaux._a_change = True

def effacer_difficulte_plateau(lot_de_plateaux: LotDePlateaux) -> None:
    "Methode qui enregistre les difficultes des plateaux et la profondeur de leur solution"
    lot_de_plateaux._ensemble_des_difficultes_de_plateaux.clear()
    lot_de_plateaux._a_change = True

def arret_des_enregistrements_de_difficultes_plateaux(lot_de_plateaux: LotDePlateaux) -> None:
    "Methode qui finalise l'arret des enregistrements des difficultes de plateaux"
    # Classement des difficultes
    cles_difficulte = list(lot_de_plateaux._ensemble_des_difficultes_de_plateaux.keys())
    if None in cles_difficulte:
        cles_difficulte.remove(None) # None est inclassable avec 'list().sort()'
    cles_difficulte_classees = copy.deepcopy(cles_difficulte)
    cles_difficulte_classees.sort()
    if cles_difficulte != cles_difficulte_classees:
        # Ordonner l'ensemble par difficulte croissante
        dico_difficulte_classe = {k: lot_de_plateaux._ensemble_des_difficultes_de_plateaux.get(k) for k in cles_difficulte_classees}
        if None in lot_de_plateaux._ensemble_des_difficultes_de_plateaux:
            dico_difficulte_classe[None] = lot_de_plateaux._ensemble_des_difficultes_de_plateaux.get(None)
        lot_de_plateaux._ensemble_des_difficultes_de_plateaux = copy.deepcopy(dico_difficulte_classe)
    
    # Classement du nombre de coups
    for difficulte, dico_nb_coups in lot_de_plateaux._ensemble_des_difficultes_de_plateaux.items():
        cles_nb_coups = list(dico_nb_coups.keys())
        if None in cles_nb_coups:
            cles_nb_coups.remove(None) # None est inclassable avec 'list().sort()'
        cles_nb_coups_classees = copy.deepcopy(cles_nb_coups)
        cles_nb_coups_classees.sort()
        if cles_nb_coups != cles_nb_coups_classees:
            # Ordonner l'ensemble par nombre de coups croissant
            dico_nb_coups_classe = {k: dico_nb_coups.get(k) for k in cles_nb_coups_classees}
            if None in lot_de_plateaux._ensemble_des_difficultes_de_plateaux.get(difficulte):
                dico_nb_coups_classe[None] = lot_de_plateaux._ensemble_des_difficultes_de_plateaux.get(difficulte).get(None)
            lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte] = copy.deepcopy(dico_nb_coups_classe)
    lot_de_plateaux.exporter_fichier_json()

