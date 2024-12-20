"Module pour créer, résoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations #, product, combinations#, combinations_with_replacement
import datetime
import json

# TODO : enregistrer les combinaisons petit à petit dans le fichier => ok
# TODO : reprendre l'enregistrement à partir du fichier.
# TODO : commencer à chercher les solutions.
#        Idée d'algo :
#          - Pour les N colonnes, créer un Thread qui vérifie si la colonne N peut-être jouée.
#          - Chaque Thread identifie les D colonnes destinations de la colonne de départ N
#          - Pour chaque colonne D, créer un Thread qui calcule le 'plateau' après le coup de la colonne N vers D.
#          - Pour les 'N x D' plateaux obtenus, calcule si la position est gagnante.
#              - GAGNANTE : Enregistre la partie et les nombres de coups dans un fichier correspondant à la position de départ
#              - BLOQUEE : s'arréter là dans la recherche.
#              - REPETEE : s'arréter là dans la recherche.
#          - Recommencer l'opération jusqu'à MAX_COUPS de profondeur

COLONNES = range(2, 7) #11
LIGNES = [2] #4
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 500_000_000


class Plateau():
    "Classe qui implémente un plateau. Son contenu et ses différentes représentations."
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
        self.__creer_les_familles()

    def __str__(self):
        if not self._str_format:
            for ligne in self.plateau_rectangle:
                self._str_format += f"{ligne}\n"
        return self._str_format

    def __eq__(self, autre):
        if not isinstance(autre, Plateau):
            # Ne sont pas comparables
            return NotImplemented
        # Comparer la taille
        if self._nb_colonnes == autre._nb_colonnes \
            or self._nb_lignes == autre._nb_lignes \
            or self._nb_colonnes_vides == autre._nb_colonnes_vides :
            return False
        # Comparer le contenu
        return self._plateau_ligne == autre._plateau_ligne

    @property
    def nb_colonnes(self):
        "Nombre de colonnes du plateau"
        return self._nb_colonnes

    @property
    def nb_lignes(self):
        "Nombre de lignes du plateau"
        return self._nb_lignes

    @property
    def nb_colonnes_vides(self):
        "Nombre de colonnes vides du plateau"
        return self._nb_colonnes_vides

    @property
    def plateau_ligne(self):
        "Représentation en 1 ligne du plateau (liste)"
        return self._plateau_ligne

    @plateau_ligne.setter
    def plateau_ligne(self, plateau_ligne):
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self._plateau_ligne = tuple(plateau_ligne)

    @property
    def plateau_ligne_texte(self):
        "Représentation en 1 ligne du plateau (texte)"
        if not self._plateau_ligne_texte:
            self.__creer_plateau_ligne_texte()
        return self._plateau_ligne_texte

    @property
    def plateau_rectangle(self):
        "Représentation en rectangle (colonnes et lignes) du plateau (liste)"
        if not self._plateau_rectangle:
            self.__creer_plateau_rectangle()
        return self._plateau_rectangle

    @property
    def plateau_rectangle_texte(self):
        "Représentation en rectangle (colonnes et lignes) du plateau (texte)"
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
        "Format du plateau utilisé pour les permutations"
        return self.plateau_ligne

    def afficher(self):
        "Afficher le plateau"
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
                self._plateau_rectangle.append(
                    self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes])

    def __creer_plateau_rectangle_texte(self):
        """"['A', 'A', 'B', 'B', ' ', ' '] => ['AA', 'BB', '  ']"""
        if self._plateau_ligne:
            self._plateau_rectangle_texte = []
            for colonne in range(self._nb_colonnes):
                self._plateau_rectangle_texte.append(''.join(
                    self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes]))

    @property
    def nb_familles(self):
        "Nombre de familles de couleurs dans le plateau"
        return self._nb_familles

    def __creer_les_familles(self):
        "Créer une liste des familles"
        if not self._liste_familles:
            self._liste_familles = [chr(ord('A')+F) for F in range(self._nb_familles) ]
        return self._liste_familles

    def creer_plateau_initial(self):
        """"Cree un plateau en ligne initial = ['A', 'A', 'B', 'B', ' ', ' ']"""
        if not self._plateau_ligne:
            self.plateau_ligne = tuple(
                [self._liste_familles[famille] for famille in range(self._nb_familles)
                                                 for membre in range(self._nb_lignes)]
                +[' ' for vide in range(self._nb_colonnes_vides)
                         for membre in range(self._nb_lignes)] )

    @property
    def est_valide(self):
        """"Verifie si le plateau en parametre est valide"""
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
        """"Verifie si le plateau actuel est gagnant"""
        return False

class LotDePlateaux():
    "Classe qui gère les lots de plateaux pour parcourir l'immensité des plateaux existants"
    def __init__(self):
        self._ensemble_des_plateaux_valides = set()
        self._ensemble_des_plateaux_a_ignorer = set()
        self._dico_compteur_des_plateaux_a_ignorer = {}
        self._nb_plateaux_max = MEMOIRE_MAX
        self._debut = datetime.datetime.now().timestamp()
        self._fin = None
        self._export_json = None
        self._nb_colonnes = None
        self._nb_lignes = None
    
    def __len__(self):
        return self.nb_plateaux_valides

    def to_dict(self):
        dict_lot_de_plateaux = {}
        if self._nb_colonnes is not None:
            dict_lot_de_plateaux['colonnes']= self._nb_colonnes
            dict_lot_de_plateaux['lignes']= self._nb_lignes

        dict_lot_de_plateaux['debut']= self.debut
        dict_lot_de_plateaux['fin']= self.fin
        if self.duree < 1:
            dict_lot_de_plateaux['duree']= f"{int(self.duree*1000)} millisecondes"
        else:
            dict_lot_de_plateaux['duree']= f"{int(self.duree)} secondes"
        
        dict_lot_de_plateaux['recherche_terminee'] = self._fin is not None

        dict_lot_de_plateaux['nombre_plateaux']= len(self.plateaux_valides)
        dict_lot_de_plateaux['liste_plateaux']= list(self.plateaux_valides)
        return dict_lot_de_plateaux

    def arret_des_enregistrements(self):
        "Méthode qui finalise la recherche de plateaux"
        self._ensemble_des_plateaux_a_ignorer.clear()
        self._dico_compteur_des_plateaux_a_ignorer.clear()
        self._fin = datetime.datetime.now().timestamp()
        self.exporter_fichier_json()

    def est_ignore(self, plateau: Plateau):
        "Retourne 'True' si le plateau est deja connu"
        if plateau.plateau_ligne_texte not in self._ensemble_des_plateaux_valides \
            and plateau.plateau_ligne_texte not in self._ensemble_des_plateaux_a_ignorer:
            # plateau.afficher()
            # Verifier que la plateau est valide
            if plateau.est_valide:
                # Enregistrer la permutation courante qui est un nouveau plateau valide
                self.__ajouter_le_plateau(plateau)
                return False
            else:
                # Nouveau Plateau invalide, on l'ignore
                self.__ignorer_le_plateau(plateau)
                return True
        self.__compter_plateau_a_ignorer(plateau)
        return True

    @property
    def plateaux_valides(self):
        "Ensemble des plateaux valides"
        return self._ensemble_des_plateaux_valides

    @property
    def nb_plateaux_valides(self):
        "Nombre de plateaux valides"
        return len(self._ensemble_des_plateaux_valides)

    @property
    def nb_plateaux_ignores(self):
        "Nombre de plateaux ignorés"
        return len(self._ensemble_des_plateaux_a_ignorer)

    @property
    def debut(self):
        "Heure de début de la recherche"
        return self._debut

    @property
    def fin(self):
        "Heure de fin (ou courante) de la recherche"
        if self._fin:
            return self._fin
        return datetime.datetime.now().timestamp()

    @property
    def duree(self):
        "Durée de la recherche"
        return self.fin - self.debut

    def __ajouter_le_plateau(self, plateau: Plateau):
        "Memorise un plateau deja traite"
        # Avec les réductions de memoires, un nouveau plateau pourrait-etre une ancienne
        # permutation effacée. Il faut vérifier les permutations avant d'ajouter définitivement
        # le plateau.
        nouveau_plateau = True
        for permutation_courante in permutations(plateau.plateau_rectangle_texte):
            plateau_a_ignorer = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
            plateau_a_ignorer.plateau_rectangle_texte = permutation_courante

            # Tester si la permutation était déjà dans les plateaux valides
            if plateau_a_ignorer.plateau_ligne_texte in self._ensemble_des_plateaux_valides:
                nouveau_plateau = False

            # Si nouveau plateau : on enregistre seulement les permutations dans 'IGNORER'
            # Sinon : on enregistre tout dans 'IGNORER'
            if not nouveau_plateau \
                or plateau_a_ignorer.plateau_ligne_texte != plateau.plateau_ligne_texte:
                self.__ignorer_le_plateau(plateau_a_ignorer)

        if nouveau_plateau:
            self._ensemble_des_plateaux_valides.add(plateau.plateau_ligne_texte)
            self._export_json.exporter(self)

    def __compter_plateau_a_ignorer(self, plateau_a_ignorer: Plateau):
        "Compte un plateau a ignorer"
        if plateau_a_ignorer.plateau_ligne_texte not in self._dico_compteur_des_plateaux_a_ignorer:
            self._dico_compteur_des_plateaux_a_ignorer[plateau_a_ignorer.plateau_ligne_texte] = 1
        else:
            self._dico_compteur_des_plateaux_a_ignorer[plateau_a_ignorer.plateau_ligne_texte] += 1

    def __ignorer_le_plateau(self, plateau_a_ignorer: Plateau):
        "Ignore un plateau et met a jour les ensembles et compteurs"
        # Ignorer le plateau
        self._ensemble_des_plateaux_a_ignorer.add(plateau_a_ignorer.plateau_ligne_texte)
        # Compter l'occurence
        self.__compter_plateau_a_ignorer(plateau_a_ignorer)
        # Optimiser la memoire
        self.__reduire_memoire()

    def __reduire_memoire(self):
        "Optimisation memoire quand la memoire maximum est atteinte"
        # Trier par valeur croissantes
        if len(self._ensemble_des_plateaux_a_ignorer) > self._nb_plateaux_max:
            print('*' * 80 + ' Réduction mémoire.')
            dico_trie_par_valeur_croissantes = dict(sorted(
                self._dico_compteur_des_plateaux_a_ignorer.items(), key=lambda item: item[1]))
            # for key, value in dico_trie_par_valeur_croissantes.items():
            #     print(f"[reduire_memoire] ({key}, {value})")

            # Vider les memoires et compteurs
            self._dico_compteur_des_plateaux_a_ignorer.clear()
            self._ensemble_des_plateaux_a_ignorer.clear()
            # print(len(self._dico_compteur_des_plateaux_a_ignorer))
            # print(len(self._ensemble_des_plateaux_a_ignorer))

            for _ in range(int(self._nb_plateaux_max/10)):
                if len(dico_trie_par_valeur_croissantes) == 0:
                    break
                # Reconduire les 10% les plus sollicites
                key, _ = dico_trie_par_valeur_croissantes.popitem()
                # print(f"[reduire_memoire] Conservation de ({key}, {_})")
                self._ensemble_des_plateaux_a_ignorer.add(key)
                self._dico_compteur_des_plateaux_a_ignorer[key] = 1
            dico_trie_par_valeur_croissantes.clear()
            # print(len(dico_trie_par_valeur_croissantes))

    def fixer_taille_memoire_max(self, nb_plateaux_max):
        "Fixe le nombre maximum de plateau a memoriser"
        if nb_plateaux_max > 0:
            self._nb_plateaux_max = nb_plateaux_max
        self.__reduire_memoire()

    def exporter_fichier_json(self):
        """Enregistre un fichier JSON avec les plateaux valides"""
        # Enregistrement des donnees dans un fichier JSON
        if self.nb_plateaux_valides > 0:
            self._export_json.forcer_export(self)

    def est_deja_termine(self, nb_colonnes, nb_lignes):
        self.__init_export_json(nb_colonnes, nb_lignes)
        data_json = self._export_json.importer()
        # TODO : Gerer le fichier absent
        # TODO : Copier le JSON dans les données de la classe
        return 'recherche_terminee' in data_json and data_json['recherche_terminee'] is True
    
    def __init_export_json(self, nb_colonnes, nb_lignes):
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        nom = f"Plateaux_{self._nb_colonnes}x{self._nb_lignes}"
        self._export_json = ExportJSON(delai=60, longueur=100, nom=nom)

class ResoudrePlateau():
    "Classe de résultion d'un plateau par parcours de toutes les possibilités de choix"
    def __init__(self, plateau_initial: Plateau):
        self._plateau_initial = plateau_initial
        self._liste_des_choix_possibles = None
        nom = f"Plateaux_{self._nb_colonnes}x{self._nb_lignes}_Resolution"
        self._export_json = ExportJSON(delai=60, longueur=100, nom=nom)

        # TODO : ResoudrePlateau().__init__()
        # Enregistrer les solutions
        # Statistiques des solutions:
        #   - la plus longue
        #   - la plus courte
        #   - la moyenne
        #   - le nombre de solution
        pass

    def __len__(self):
        # TODO : implémenter la longueur = nombre de solutions trouvées
        pass
        return 0

    def to_dict(self):
        # TODO : implémenter la conversion de la classe en dictionnaire pour l'enregistrement JSON
        pass
        return dict()

    def __ensemble_des_choix_possibles(self):
        "Liste tous les choix possible pour un plateau (valide et invalides)"
        if not self._liste_des_choix_possibles:
            # Liste de tous les possibles à construire selon la dimension du plateau
            self._liste_des_choix_possibles = []
            for depart in range(self._plateau_initial.nb_colonnes):
                for arrivee in range(self._plateau_initial.nb_colonnes):
                    if depart != arrivee:
                        self._liste_des_choix_possibles.append(list(depart, arrivee))
        # Nombre de choix = (nb_colonnes * (nb_colonnes-1))
        return self._liste_des_choix_possibles

    def __ajouter_choix(self, plateau: Plateau, choix):
        "Enregistre un choix et modifie le plateau selon ce choix"
        # Enregistrer le choix
        # Modifier le plateau
        return True

    def __retirer_choix(self, plateau: Plateau, choix):
        "Annule le dernier choix et restaure le plateau precedent"
        # TODO : ResoudrePlateau().__retirer_choix()
        # Attention : il faut trouver comment identifier les couleurs à laisser
        #             dans la colonne d'arrivée pour 'retirer le choix'.
        return True

    def __est_valide(self, plateau: Plateau, choix):
        "Vérifie la validité du choix"
        # TODO : ResoudrePlateau().__est_valide()
        # INVALIDE Si les colonnes de départ et d'arrivée sont identiques
        # INVALIDE Si la colonne de départ est vide
        # INVALIDE Si la colonne de départ est pleine et monocouleur
        # INVALIDE Si la colonne d'arrivée est pleine
        # INVALIDE Si la colonne d'arrivée n'a pas la même couleur au sommet
        # INVALIDE Si la colonne d'arrivée n'a pas assez de place
        return True

    def __solution_complete(self, plateau: Plateau):
        "Evalue si le plateau est terminé (gagné ou bloqué)"
        if plateau.a_gagne():
            # TODO : ResoudrePlateau().__solution_complete()
            # Gagné si toutes les colonnes sont pleines ou vides
            #    ET que les colonnes pleines soient monocouleurs
            pass

        # Peut-etre des tableaux "bloqués"
        return True

    def __enregistrer_solution(self, plateau: Plateau):
        "Enregistre le parcours de la solution pour la restituer"
        # TODO : ResoudrePlateau().__enregistrer_solution()
        #        Enregistrer solution complet + màj statistiques
        self._export_json.exporter(self)
        pass

    def backtracking(self, plateau: Plateau):
        "Parcours de tous les choix afin de débusquer toutes les solutions"
        if self.__solution_complete(plateau):   # Condition d'arrêt
            self.__enregistrer_solution(plateau)
            return

        for choix in self.__ensemble_des_choix_possibles():
            if self.__est_valide(plateau, choix):  # Vérifier si le choix est valide
                self.__ajouter_choix(plateau, choix)  # Prendre ce choix
                self.backtracking(plateau)  # Appeler récursivement la fonction
                self.__retirer_choix(plateau, choix)  # Annuler le choix (retour en arrière)

    def exporter_fichier_json(self):
        """Enregistre un fichier JSON avec les solutions et les statistiques du plateau"""
        self._export_json.forcer_export(self)
        pass

    @property
    def nb_solutions(self):
        # TODO : ResoudrePlateau().nb_solutions
        pass

    @property
    def solution_la_plus_courte(self):
        # TODO : ResoudrePlateau().solution_la_plus_courte
        pass

    @property
    def solution_la_plus_longue(self):
        # TODO : ResoudrePlateau().solution_la_plus_longue
        pass

    @property
    def solution_moyenne(self):
        # TODO : ResoudrePlateau().solution_moyenne
        pass

class ExportJSON():
    def __init__(self, delai, longueur, nom):
        self._delai_enregistrement = delai
        self._longueur_enregistrement = longueur
        self._nom_enregistrement = nom

        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        self._longueur_dernier_enregistrement = 0

    def exporter(self, contenu):
        """Enregistre un fichier JSON selon des critères de nombres et de temps"""
        if (len(contenu) - self._longueur_dernier_enregistrement >= self._longueur_enregistrement):
            self.forcer_export(contenu)

        if (datetime.datetime.now().timestamp() - self._timestamp_dernier_enregistrement >= self._delai_enregistrement) \
            and (len(contenu) > self._longueur_dernier_enregistrement):
            self.forcer_export(contenu)

    def forcer_export(self, contenu):
        """Enregistre un fichier JSON en ignorant les critères"""
        # Enregistrement des donnees dans un fichier JSON
        with open(self._nom_enregistrement+".json", "w", encoding='utf-8') as fichier:
            json.dump(contenu.to_dict(), fichier, ensure_ascii=False)
        self._longueur_dernier_enregistrement = len(contenu)
        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()

    def importer(self):
        """Lit dans un fichier JSON les informations totales ou de la dernière itération réalisée."""
        try:
            with open(self._nom_enregistrement+".json", "r", encoding='utf-8') as fichier:
                dico_json = json.load(fichier)
            return dico_json
        except FileNotFoundError:
            return {}

for lignes in LIGNES:
    for colonnes in COLONNES:
        print(f"*** Generatrice {colonnes}x{lignes}: DEBUT")
        plateau = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
        plateau.creer_plateau_initial()
        plateau.afficher()
        lot_de_plateaux = LotDePlateaux()
        if not lot_de_plateaux.est_deja_termine(colonnes, lignes):
            # lot_de_plateaux.fixer_taille_memoire_max(5)
            for permutation_courante in permutations(plateau.pour_permutations):
                # Verifier que ce plateau est nouveau
                plateau_courant = Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
                plateau_courant.plateau_ligne = permutation_courante
                if not lot_de_plateaux.est_ignore(plateau_courant):
                    if lot_de_plateaux.nb_plateaux_valides % 400 == 0:
                        print(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")

            lot_de_plateaux.arret_des_enregistrements()
            # lot_de_plateaux.exporter_fichier_json()
            if (lot_de_plateaux.duree) < 10:
                print(f"*** Generatrice {colonnes}x{lignes}: FIN en {
                    int((lot_de_plateaux.duree)*1000)} millisecondes")
            else:
                print(f"*** Generatrice {colonnes}x{lignes}: FIN en {
                    int(lot_de_plateaux.duree)} secondes")
        else:
            print("Ce lot de plateaux est déjà terminé")

        print(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
        print(f"nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
