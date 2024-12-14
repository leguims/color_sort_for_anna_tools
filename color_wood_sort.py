from itertools import permutations #, product, combinations#, combinations_with_replacement
import datetime
import json


COLONNES = range(2, 5) #11
LIGNES = [2] #4
COLONNES_VIDES_MAX = 1

def afficher_heure():
    "Fonction pour obtenir et afficher l'heure actuelle"
    # Obtention de l'heure actuelle
    heure_actuelle = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("L'heure actuelle est :", heure_actuelle)

def enregistrer_plateaux_ligne(plateaux_ligne, nb_colonnes, nb_lignes, debut=None, fin=None):
    """"plateaux_ligne = [['A', 'A', 'B', 'B', ' ', ' ', 'B', 'A', 'B', 'A', ' ', ' ']]
     enregistrement plateaux_lignes_string = ['AABB  ', 'BABA  ']"""
    infos_plateau = {}
    infos_plateau['COLONNES']= nb_colonnes
    infos_plateau['LIGNES']= nb_lignes
    if debut:
        infos_plateau['debut']= debut
    if fin:
        infos_plateau['fin']= fin
    if debut and fin:
        infos_plateau['duree']= int(fin - debut)
    infos_plateau['nombre_plateaux']= len(plateaux_ligne)
    infos_plateau['liste_plateaux']= []
    for p in plateaux_ligne:
        # Convertir le plateau en une chaine de caracteres
        plateau_string = ''.join(p)
        #infos_plateau['liste_plateaux'].append(list(p))
        infos_plateau['liste_plateaux'].append(plateau_string)

    # Enregistrement des donnees dans un fichier JSON
    with open(f"Plateaux_{nb_colonnes}x{nb_lignes}.json", "w", encoding='utf-8') as fichier:
        #json.dump(infos_plateau, fichier, ensure_ascii=False, indent=4)
        json.dump(infos_plateau, fichier, ensure_ascii=False)

def lire_heure():
    return datetime.datetime.now().timestamp()

def afficher_plateau(plateau_rectangle):
    """"plateau_rectangle = [['A', 'A'], ['B', 'B], [' ', ' ']]"""
    for ligne in plateau_rectangle:
        print(ligne)

def obtenir_nombre_de_membres_de_famille(nb_colonnes, nb_lignes, nb_colonnes_vides):
    return nb_lignes

def obtenir_nombre_de_famille(nb_colonnes, nb_lignes, nb_colonnes_vides):
    return nb_colonnes - nb_colonnes_vides

def creer_les_familles(nb_colonnes, nb_lignes, nb_colonnes_vides):
    nb_familles = obtenir_nombre_de_famille(
        nb_colonnes, nb_lignes, nb_colonnes_vides)
    return [chr(ord('A')+F) for F in range(nb_familles) ]

def creer_plateau_ligne_string_initial(nb_colonnes, nb_lignes, nb_colonnes_vides):
    """"retourne plateau_ligne_string_initial = ['AABB  ']"""
    plateau_ligne_string_initial = str()
    liste_familles = creer_les_familles(nb_colonnes, nb_lignes, nb_colonnes_vides)
    for colonne in range(nb_colonnes-nb_colonnes_vides):
        plateau_ligne_string_initial += liste_familles[colonne]*nb_lignes
    for colonne in range(nb_colonnes_vides):
        plateau_ligne_string_initial += ' '*nb_lignes
    return plateau_ligne_string_initial

def valider_plateau_ligne(plateau_ligne, nb_colonnes, nb_lignes):
    """"plateau_ligne = ['A', 'A', 'B', 'B, ' ', ' ']"""
    # Pour chaque colonne, les cases vides sont sur les dernieres cases
    for colonne in range(nb_colonnes):
        case_vide_presente = False
        for ligne in range(nb_lignes):
            if not case_vide_presente:
                # Chercher la premiere case vide de la colonne
                if plateau_ligne[colonne * nb_lignes + ligne] == ' ':
                    case_vide_presente = True
            else:
                # Toutes les autres case de la lignes doivent etre vides
                if plateau_ligne[colonne * nb_lignes + ligne] != ' ':
                    return False
    return True

def convertir_plateau_ligne_en_ligne_string(plateau_ligne, nb_colonnes, nb_lignes):
    """"plateau_ligne = ['A', 'A', 'B', 'B', ' ', ' ']
      =>
      plateau_ligne_string = ['AABB  ']
    """
    return ''.join(plateau_ligne)

def convertir_plateau_ligne_en_rectangle(plateau_ligne, nb_colonnes, nb_lignes):
    """"plateau_ligne = ['A', 'A', 'B', 'B', ' ', ' ']
      =>
      plateau_en_rectangle = [['A', 'A'], ['B', 'B'], [' ', ' ']]
    """
    plateau_rectangle = []
    for colonne in range(nb_colonnes):
        plateau_rectangle.append(plateau_ligne[colonne*nb_lignes : colonne*nb_lignes + nb_lignes])
    return plateau_rectangle

def convertir_plateau_ligne_en_rectangle_string(plateau_ligne, nb_colonnes, nb_lignes):
    """"plateau_ligne = ['A', 'A', 'B', 'B', ' ', ' ']
      =>
      plateau_rectangle_string = ['AA', 'BB', '  ']
    """
    plateau_rectangle_string = []
    for colonne in range(nb_colonnes):
        plateau_rectangle_string.append(''.join(plateau_ligne[colonne*nb_lignes : colonne*nb_lignes + nb_lignes]))
    return plateau_rectangle_string

def convertir_plateau_rectangle_string_en_ligne(plateau_rectangle_string, nb_colonnes, nb_lignes):
    """"plateau_rectangle_string = ['AA', 'BB', '  ']
      =>
      plateau_ligne = ['A', 'A', 'B', 'B', ' ', ' ']
    """
    plateau_ligne = []
    for colonne_str in plateau_rectangle_string:
        for c in colonne_str:
            plateau_ligne.append(c)
    return tuple(plateau_ligne)

def convertir_plateau_ligne_string_en_rectangle_string(plateau_ligne_string, nb_colonnes, nb_lignes):
    """"plateau_ligne_string = ['AABB  ']
      => 
      plateau_rectangle_string = ['AA', 'BB', '  ']]"""
    plateau_rectangle_string = []
    for colonne in range(nb_colonnes):
        plateau_rectangle_string.append(''.join(plateau_ligne_string[colonne*nb_lignes : colonne*nb_lignes + nb_lignes]))
    return plateau_rectangle_string

def convertir_plateau_rectangle_string_en_ligne_string(plateau_rectangle_string, nb_colonnes, nb_lignes):
    """"plateau_rectangle_string = ['AA', 'BB', '  ']]
      =>
      plateau_ligne_string = ['AABB  ']
    """
    return ''.join(plateau_rectangle_string)

def compter_membres(plateau_rectangle, nom):
    compteur = 0
    for i in plateau_rectangle:
        compteur += i.count(nom)
    return compteur

for lignes in LIGNES:
    for colonnes in COLONNES:
        print(f"*** Generatrice {colonnes}x{lignes}: DEBUT")
        debut = lire_heure()
        afficher_heure()
        plateau_ligne_string_initial = creer_plateau_ligne_string_initial(colonnes, lignes, COLONNES_VIDES_MAX)
        plateau_initial_rectangle = convertir_plateau_ligne_string_en_rectangle_string(plateau_ligne_string_initial, colonnes, lignes)
        afficher_plateau(plateau_initial_rectangle)
        loop_plateau_ligne = set()
        loop_plateau_ligne_a_ignorer = set()
        for plateau in permutations(plateau_ligne_string_initial):
            # Vérifier que ce plateau est nouveau
            if plateau not in loop_plateau_ligne and plateau not in loop_plateau_ligne_a_ignorer:
                # Verifier que les cases vides sont bien placees (en fin de colonne uniquement)
                if valider_plateau_ligne(plateau, colonnes, lignes):
                    loop_plateau_ligne.add(plateau)
                    # Ignorer toutes les permutations de ce plateau
                    plateau_rectangle_string = convertir_plateau_ligne_en_rectangle_string(plateau, colonnes, lignes)
                    for ignorer_plateau_string in permutations(plateau_rectangle_string):
                        ignorer_plateau = convertir_plateau_rectangle_string_en_ligne(ignorer_plateau_string, colonnes, lignes)
                        if ignorer_plateau != plateau:
                            loop_plateau_ligne_a_ignorer.add(ignorer_plateau)
                    if len(loop_plateau_ligne)%400 == 0:
                        print(f"len(loop_plateau_ligne)={len(loop_plateau_ligne)}")
                else:
                    loop_plateau_ligne_a_ignorer.add(plateau)

        print(f"len(loop_plateau_ligne) = {len(loop_plateau_ligne)}")
        print(f"len(loop_plateau_ligne_a_ignorer) = {len(loop_plateau_ligne_a_ignorer)}")
        loop_plateau_ligne_a_ignorer.clear()
        fin = lire_heure()
        enregistrer_plateaux_ligne(loop_plateau_ligne, colonnes, lignes, debut, fin)
        print(f"*** Generatrice {colonnes}x{lignes}: FIN")
