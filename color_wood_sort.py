from itertools import permutations, product, combinations#, combinations_with_replacement

COLONNES = 5 #11
LIGNES = 2 #4
COLONNES_VIDES_MAX = 1
NB_FAMILLES = COLONNES - COLONNES_VIDES_MAX

FAMILLES = [chr(ord('A')+F) for F in range(NB_FAMILLES) ]
nb_cases = COLONNES * LIGNES
nb_cases_vides = COLONNES_VIDES_MAX * LIGNES

def afficher_plateau(plateau):
    for ligne in plateau:
        print(ligne)

def creer_plateau_initial_ligne(nb_colonnes, nb_lignes, nb_colonnes_vides):
    plateau_initial_ligne = []
    for colonne in range(nb_colonnes-nb_colonnes_vides):
        for ligne in range(nb_lignes):
            plateau_initial_ligne.append(FAMILLES[colonne])
    for colonne in range(nb_colonnes_vides):
        for ligne in range(nb_lignes):
            plateau_initial_ligne.append(' ')
    return plateau_initial_ligne

def valider_plateau_ligne(plateau, nb_colonnes, nb_lignes):
    # Pour chaque colonne, les cases vides sont sur les dernières cases
    for colonne in range(nb_colonnes):
        case_vide_presente = False
        for ligne in range(nb_lignes):
            if not case_vide_presente:
                # Chercher la premiere case vide de la colonne
                if plateau[colonne * nb_lignes + ligne] == ' ':
                    case_vide_presente = True
            else:
                # Toutes les autres case de la lignes doivent être vides
                if plateau[colonne * nb_lignes + ligne] != ' ':
                    #print("erreur")
                    #afficher_plateau(convertir_plateau_plat_en_rectangle(plateau, nb_colonnes, nb_lignes))
                    return False
    return True

def convertir_plateau_plat_en_rectangle(plateau, nb_colonnes, nb_lignes):
    plateau_rectangle = []
    for colonne in range(nb_colonnes):
        plateau_rectangle.append(plateau[colonne*nb_lignes : colonne*nb_lignes + nb_lignes])
    return plateau_rectangle

def compter_membres(plateau, nom):
    compteur = 0
    for i in plateau:
        compteur += i.count(nom)
    return compteur

#def convertir_

PLATEAU = [
    ['A','A','A','B'],
    ['B','B','B','A'],
    ['C','C','C','D'],
    ['D','D','D','C'],
    ['E','E','E','F'],
    ['F','F','F','E'],
    ['G','G','G','H'],
    ['H','H','H','I'],
    ['I','I','I','G'],
    [' ',' ',' ',' '],
    [' ',' ',' ',' ']    
    ]
print(f"PLATEAU =\n{PLATEAU}")
afficher_plateau(PLATEAU)

plateau_initial_ligne = creer_plateau_initial_ligne(COLONNES, LIGNES, COLONNES_VIDES_MAX)
print(f"len(plateau_initial_ligne) = {len(plateau_initial_ligne)}")
print(f"plateau_initial_ligne =\n{plateau_initial_ligne}")
plateau_initial_rectangle = convertir_plateau_plat_en_rectangle(plateau_initial_ligne, COLONNES, LIGNES)
print(f"plateau_initial_rectangle =\n{plateau_initial_rectangle}")
afficher_plateau(plateau_initial_rectangle)

print("Génératrice : DEBUT")
loop_plateau_ligne = set()
loop_plateau_ligne_invalide = set()
for plateau in permutations(plateau_initial_ligne):
    #plateau_rectangle = convertir_plateau_plat_en_rectangle(plateau, COLONNES, LIGNES)
    #afficher_plateau(plateau_rectangle)
    if plateau not in loop_plateau_ligne and plateau not in loop_plateau_ligne_invalide:
        #print("ok")
        #plateau_rectangle = convertir_plateau_plat_en_rectangle(plateau, COLONNES, LIGNES)
        #afficher_plateau(plateau_rectangle)

        # Vérifier que les cases vides sont bien placées (en fin de colonne uniquement)
        if valider_plateau_ligne(plateau, COLONNES, LIGNES):
            loop_plateau_ligne.add(plateau)
            if len(loop_plateau_ligne)%400 == 0:
                print(f"len(loop_plateau_ligne)={len(loop_plateau_ligne)}")
                #plateau_rectangle = convertir_plateau_plat_en_rectangle(plateau, COLONNES, LIGNES)
                #afficher_plateau(plateau_rectangle)
        else:
            loop_plateau_ligne_invalide.add(plateau)

print(f"len(loop_plateau_ligne) = {len(loop_plateau_ligne)}")
print(f"len(loop_plateau_ligne_invalide) = {len(loop_plateau_ligne_invalide)}")
loop_plateau_ligne_invalide.clear()
print("Génératrice : FIN")


#permut_initial = [tuple(i) for i in permutations(plateau_initial_ligne)]
#permut_initial_set = set(permut_initial)
#print(f"taille initiale permut = {len(permut_initial)}")
#print(f"taille initiale set(permut) = {len(permut_initial_set)}")




#print(f"loop_plateau_ligne =\n{loop_plateau_ligne}")
#afficher_plateau(loop_plateau_ligne)

#for colonne in range(COLONNES):
    
