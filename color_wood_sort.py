from itertools import permutations #, product, combinations#, combinations_with_replacement
import datetime
import json


COLONNES = range(2, 6) #11
LIGNES = [2] #4
COLONNES_VIDES_MAX = 1


class Plateau():
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides=1):
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._est_valide = None
        # plateau_ligne : ['A', 'A', 'B', 'B', ' ', ' ']
        self._plateau_ligne = None
        # plateau_ligne_texte : ['AABB  ']
        self._plateau_ligne_texte = None
        # plateau_rectangle : [['A', 'A'], ['B', 'B]', [' ', ' ']]
        self._plateau_rectangle = None
        # plateau_rectangle_texte : ['AA', 'BB', '  ']
        self._plateau_rectangle_texte = None
        self._str_format = ""
        self._nb_familles = nb_colonnes - nb_colonnes_vides
        self._liste_familles = []
    
    def __str__(self):
        if not self._str_format:
            for ligne in self.plateau_rectangle:
                self._str_format += f"{ligne}\n"
        return self._str_format

    @property
    def plateau_ligne(self):
        return self._plateau_ligne

    @plateau_ligne.setter
    def plateau_ligne(self, plateau_ligne):
        # Pas de vérification sur la validité,
        # pour pouvoir traiter les plateaux invalides
        # à ignorer.
        self._plateau_ligne = tuple(plateau_ligne)

    @property
    def plateau_ligne_texte(self):
        if not self._plateau_ligne_texte:
            self.__creer_plateau_ligne_texte()
        return self._plateau_ligne_texte

    @property
    def plateau_rectangle(self):
        if not self._plateau_rectangle:
            self.__creer_plateau_rectangle()
        return self._plateau_rectangle

    @property
    def plateau_rectangle_texte(self):
        if not self._plateau_rectangle_texte:
            self.__creer_plateau_rectangle_texte()
        return self._plateau_rectangle_texte

    @plateau_rectangle_texte.setter
    def plateau_rectangle_texte(self, plateau_rectangle_texte):
        # Rectangle_texte => plateau_ligne_texte
        plateau_ligne_texte = ''.join(plateau_rectangle_texte)
        # plateau_ligne_texte => plateau_ligne
        self.plateau_ligne = [c for c in plateau_ligne_texte]

    @property
    def pour_permutations(self):
        return self.plateau_ligne

    def afficher(self):
        print(self)

    def __creer_plateau_ligne_texte(self):
        """['A', 'A', 'B', 'B', ' ', ' '] => ['AABB  ']"""
        if self._plateau_ligne:
            self._plateau_ligne_texte = ''.join(self._plateau_ligne)

    def __creer_plateau_rectangle(self):
        """"['A', 'A', 'B', 'B', ' ', ' '] => [['A', 'A'], ['B', 'B'], [' ', ' ']]"""
        if self._plateau_ligne:
            self._plateau_rectangle = []
            for colonne in range(self._nb_colonnes):
                self._plateau_rectangle.append(self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes])

    def __creer_plateau_rectangle_texte(self):
        """"['A', 'A', 'B', 'B', ' ', ' '] => ['AA', 'BB', '  ']"""
        if self._plateau_ligne:
            self._plateau_rectangle_texte = []
            for colonne in range(self._nb_colonnes):
                self._plateau_rectangle_texte.append(''.join(self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes]))

    @property
    def nb_familles(self):
        return self._nb_familles

    def creer_les_familles(self):
        if not self._liste_familles:
            self._liste_familles = [chr(ord('A')+F) for F in range(self._nb_familles) ]
        return self._liste_familles

    def creer_plateau_initial(self):
        """"Crée un plateau en ligne initial = ['A', 'A', 'B', 'B', ' ', ' ']"""
        if not self._plateau_ligne:
            liste_familles = self.creer_les_familles()
            self.plateau_ligne = tuple(
                [self._liste_familles[famille] for famille in range(self._nb_familles) for membre in range(self._nb_lignes)]
                +[' ' for vide in range(self._nb_colonnes_vides) for membre in range(self._nb_lignes)] )

    @property
    def est_valide(self):
        """"Vérifie si le plateau en parametre est valide"""
        if self._plateau_ligne and self._est_valide is None:
            # Pour chaque colonne, les cases vides sont sur les dernieres cases
            case_vide = ' '
            for colonne in range(self._nb_colonnes):
                case_vide_presente = False
                for ligne in range(self._nb_lignes):
                    if not case_vide_presente:
                        # Chercher la premiere case vide de la colonne
                        if self.plateau_ligne[colonne * self._nb_lignes + ligne] == case_vide:
                            case_vide_presente = True
                    else:
                        # Toutes les autres case de la lignes doivent etre vides
                        if self.plateau_ligne[colonne * self._nb_lignes + ligne] != case_vide:
                            self._est_valide = False
                            return self._est_valide
            self._est_valide = True
        return self._est_valide

    def a_gagne(self):
        """"Vérifie si le plateau actuel est gagnant"""
        return False


def afficher_heure():
    "Fonction pour obtenir et afficher l'heure actuelle"
    # Obtention de l'heure actuelle
    heure_actuelle = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("L'heure actuelle est :", heure_actuelle)

def lire_heure():
    return datetime.datetime.now().timestamp()

def enregistrer_la_liste_de_plateaux_ligne(plateaux_ligne_texte, nb_colonnes, nb_lignes, debut=None, fin=None):
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
    infos_plateau['nombre_plateaux']= len(plateaux_ligne_texte)
    infos_plateau['liste_plateaux']= list(plateaux_ligne_texte)

    # Enregistrement des donnees dans un fichier JSON
    with open(f"Plateaux_{nb_colonnes}x{nb_lignes}.json", "w", encoding='utf-8') as fichier:
        #json.dump(infos_plateau, fichier, ensure_ascii=False, indent=4)
        json.dump(infos_plateau, fichier, ensure_ascii=False)

def ajouter_les_permutations(plateau_ligne_texte, plateau_rectangle_texte, liste_plateau):
    for permutation_courante in permutations(plateau_rectangle_texte):
        plateau_a_ignorer = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
        plateau_a_ignorer.plateau_rectangle_texte = permutation_courante
        if plateau_a_ignorer.plateau_ligne_texte != plateau_ligne_texte:
            liste_plateau.add(plateau_a_ignorer.plateau_ligne_texte)


for lignes in LIGNES:
    for colonnes in COLONNES:
        print(f"*** Generatrice {colonnes}x{lignes}: DEBUT")
        debut = lire_heure()
        afficher_heure()
        plateau = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
        plateau.creer_plateau_initial()
        plateau.afficher()
        ensemble_des_plateaux_valides = set()
        ensemble_des_plateaux_a_ignorer = set()
        for permutation_courante in permutations(plateau.pour_permutations):
            # Vérifier que ce plateau est nouveau
            permutation_courante_texte = ''.join(permutation_courante)
            if permutation_courante_texte not in ensemble_des_plateaux_valides and permutation_courante_texte not in ensemble_des_plateaux_a_ignorer:
                # Vérifier que la permutation courante est un plateau valide
                plateau_courant = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
                plateau_courant.plateau_ligne = permutation_courante
                # plateau_courant.afficher()
                if plateau_courant.est_valide:
                    # Enregistrer la permutation courante qui est un plateau valide
                    ensemble_des_plateaux_valides.add(plateau_courant.plateau_ligne_texte)
                    if len(ensemble_des_plateaux_valides)%400 == 0:
                        print(f"len(ensemble_des_plateaux_valides)={len(ensemble_des_plateaux_valides)}")
                else:
                    # Plateau invalide, on l'ignore
                    ensemble_des_plateaux_a_ignorer.add(plateau_courant.plateau_ligne_texte)
                # Ignorer toutes les permutations de ce plateau
                ajouter_les_permutations(plateau_courant.plateau_ligne_texte,
                                         plateau_courant.plateau_rectangle_texte,
                                         ensemble_des_plateaux_a_ignorer)

        print(f"len(ensemble_des_plateaux_valides) = {len(ensemble_des_plateaux_valides)}")
        print(f"len(ensemble_des_plateaux_a_ignorer) = {len(ensemble_des_plateaux_a_ignorer)}")
        ensemble_des_plateaux_a_ignorer.clear()
        fin = lire_heure()
        enregistrer_la_liste_de_plateaux_ligne(ensemble_des_plateaux_valides, colonnes, lignes, debut, fin)
        print(f"*** Generatrice {colonnes}x{lignes}: FIN")
