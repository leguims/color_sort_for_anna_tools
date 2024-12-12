from itertools import permutations, product, combinations#, combinations_with_replacement
import datetime
import json


COLONNES = range(2, 11) #11
LIGNES = [2] #4
COLONNES_VIDES_MAX = 1

def afficher_heure():
    "Fonction pour obtenir et afficher l'heure actuelle"
    # Obtention de l'heure actuelle
    heure_actuelle = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("L'heure actuelle est :", heure_actuelle)

def enregistrer_plateaux(plateau, nb_colonnes, nb_lignes, debut=None, fin=None):
    infos_plateau = {}
    infos_plateau['COLONNES']= nb_colonnes
    infos_plateau['LIGNES']= nb_lignes
    if debut:
        infos_plateau['debut']= debut
    if fin:
        infos_plateau['fin']= fin
    if debut and fin:
        infos_plateau['duree']= int(fin - debut)
    infos_plateau['nombre_plateaux']= len(plateau)
    infos_plateau['liste_plateaux']= []
    for p in plateau:
        # Convertir le plateau en une chaine de caracteres
        plateau_string = ''.join(p)
        #infos_plateau['liste_plateaux'].append(list(p))
        infos_plateau['liste_plateaux'].append(plateau_string)

    # Enregistrement des données dans un fichier JSON
    with open(f"Plateaux_{nb_colonnes}x{nb_lignes}.json", "w", encoding='utf-8') as fichier:
        #json.dump(infos_plateau, fichier, ensure_ascii=False, indent=4)
        json.dump(infos_plateau, fichier, ensure_ascii=False)

def lire_heure():
    return datetime.datetime.now().timestamp()

def afficher_plateau(plateau):
    for ligne in plateau:
        print(ligne)

def obtenir_nombre_de_membres_de_famille(nb_colonnes, nb_lignes, nb_colonnes_vides):
    return nb_lignes

def obtenir_nombre_de_famille(nb_colonnes, nb_lignes, nb_colonnes_vides):
    return nb_colonnes - nb_colonnes_vides

def creer_les_familles(nb_colonnes, nb_lignes, nb_colonnes_vides):
    nb_familles = obtenir_nombre_de_famille(
        nb_colonnes, nb_lignes, nb_colonnes_vides)
    return [chr(ord('A')+F) for F in range(nb_familles) ]

def creer_plateau_initial_ligne(nb_colonnes, nb_lignes, nb_colonnes_vides):
    plateau_initial_ligne = str()
    liste_familles = creer_les_familles(nb_colonnes, nb_lignes, nb_colonnes_vides)
    for colonne in range(nb_colonnes-nb_colonnes_vides):
        plateau_initial_ligne += liste_familles[colonne]*nb_lignes
    for colonne in range(nb_colonnes_vides):
        plateau_initial_ligne += ' '*nb_lignes
    return plateau_initial_ligne

def valider_plateau_ligne(plateau, nb_colonnes, nb_lignes):
    # Pour chaque colonne, les cases vides sont sur les derniÃ¨res cases
   for colonne in range(nb_colonnes):
        case_vide_presente = False
        for ligne in range(nb_lignes):
            if not case_vide_presente:
                # Chercher la premiere case vide de la colonne
                if plateau[colonne * nb_lignes + ligne] == ' ':
                    case_vide_presente = True
            else:
                # Toutes les autres case de la lignes doivent Ãªtre vides
                if plateau[colonne * nb_lignes + ligne] != ' ':
                    return False
    return True

def convertir_plateau_plat_en_rectangle(plateau, nb_colonnes, nb_lignes):
    plateau_rectangle = []
    for colonne in range(nb_colonnes):
        plateau_rectangle.append(plateau[colonne*nb_lignes : colonne*nb_lignes + nb_lignes])
    return plateau_rectangle

def compter_membres(plateau_rectangle, nom):
    compteur = 0
    for i in plateau_rectangle:
        compteur += i.count(nom)
    return compteur


for lignes in LIGNES:
    for colonnes in COLONNES:
        print(f"*** Génératrice {colonnes}x{lignes}: DEBUT")
        debut = lire_heure()
        afficher_heure()
        plateau_initial_ligne = creer_plateau_initial_ligne(colonnes, lignes, COLONNES_VIDES_MAX)
        plateau_initial_rectangle = convertir_plateau_plat_en_rectangle(plateau_initial_ligne, colonnes, lignes)
        afficher_plateau(plateau_initial_rectangle)
        loop_plateau_ligne = set()
        loop_plateau_ligne_invalide = set()
        for plateau in permutations(plateau_initial_ligne):
            if plateau not in loop_plateau_ligne and plateau not in loop_plateau_ligne_invalide:
                # Vérifier que les cases vides sont bien placées (en fin de colonne uniquement)
                if valider_plateau_ligne(plateau, colonnes, lignes):
                    loop_plateau_ligne.add(plateau)
                    if len(loop_plateau_ligne)%400 == 0:
                        print(f"len(loop_plateau_ligne)={len(loop_plateau_ligne)}")
                else:
                    loop_plateau_ligne_invalide.add(plateau)

        print(f"len(loop_plateau_ligne) = {len(loop_plateau_ligne)}")
        print(f"len(loop_plateau_ligne_invalide) = {len(loop_plateau_ligne_invalide)}")
        loop_plateau_ligne_invalide.clear()
        fin = lire_heure()
        enregistrer_plateaux(loop_plateau_ligne, colonnes, lignes, debut, fin)
        print(f"*** Génératrice {colonnes}x{lignes}: FIN")
